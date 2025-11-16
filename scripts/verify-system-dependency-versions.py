#!/usr/bin/env python3
"""Verify installed system dependency versions match pinned versions.

This script can be called from:
- Installation scripts (bash/PowerShell) - to verify after installation
- pytest config (Python) - to verify before running tests

Usage:
    # From bash/PowerShell:
    python3 scripts/verify-system-dependency-versions.py

    # From Python:
    from scripts.verify_system_dependency_versions import verify_dependency_versions
    verify_dependency_versions()
"""

import sys
from pathlib import Path

# Add project root to path so we can import audiometa modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from audiometa.utils.os_dependencies_checker import get_dependencies_checker  # noqa: E402
from audiometa.utils.os_dependencies_checker.config import load_dependencies_pinned_versions  # noqa: E402


def verify_dependency_versions() -> int:
    """Verify system dependency versions match pinned versions.

    Returns:
        0 if all versions match, 1 if there are mismatches
    """
    pinned_versions = load_dependencies_pinned_versions()

    if not pinned_versions:
        config_path = project_root / "system-dependencies.toml"
        sys.stderr.write(f"ERROR: Failed to load system-dependencies.toml from {config_path}\n")
        sys.stderr.write("File not found or cannot be parsed.\n")
        return 1

    checker = get_dependencies_checker()
    if not checker:
        sys.stderr.write("ERROR: Unsupported OS or dependencies checker not available\n")
        return 1

    os_type = checker.get_os_type()
    has_errors = False
    errors = []

    for tool, versions in pinned_versions.items():
        expected_version = versions.get(os_type)
        if not expected_version:
            continue

        # Skip optional tools on Windows
        if os_type == "windows" and tool in ["id3v2", "mediainfo", "exiftool"]:
            continue

        # Get installed version using OS-specific checker
        package = "media-info" if tool == "mediainfo" and os_type == "macos" else tool
        installed = checker.get_installed_version(package, expected_version=expected_version)

        # Check if tool is available
        tool_command = "ffprobe" if tool == "ffmpeg" else tool
        if not checker.check_tool_available(tool_command):
            if not installed:
                errors.append(f"{tool}: NOT INSTALLED")
            else:
                errors.append(f"{tool}: INSTALLED BUT NOT IN PATH (version {installed} detected via package manager)")
            has_errors = True
            continue

        # Verify version matches using checker's version comparison logic
        if not installed:
            errors.append(f"{tool}: VERSION CHECK FAILED (pinned version not found)")
            has_errors = True
            continue

        # Use checker's version matching logic (handles OS-specific normalization)
        if not checker._versions_match(expected_version, installed):
            errors.append(f"{tool}: version mismatch (expected {expected_version}, got {installed})")
            has_errors = True

    if has_errors:
        sys.stderr.write("\n" + "=" * 80 + "\n")
        sys.stderr.write("ERROR: System dependency version verification failed\n")
        sys.stderr.write("=" * 80 + "\n\n")
        sys.stderr.write("The following dependencies have version mismatches or are missing:\n\n")
        for error in errors:
            sys.stderr.write(f"  - {error}\n")
        sys.stderr.write(
            "\nTo fix:\n"
            "  1. Update system-dependencies.toml with correct versions\n"
            "  2. Update scripts/install-system-dependencies-*.sh if needed\n"
            "  3. Re-run the installation script\n"
        )
        sys.stderr.write("\nThis ensures tests use the same tool versions as CI.\n")
        sys.stderr.write("\n" + "=" * 80 + "\n")
        return 1

    return 0


def main():
    """Main entry point for command-line usage."""
    exit_code = verify_dependency_versions()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
