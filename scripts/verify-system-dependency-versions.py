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

import importlib.util
import sys
import types
from importlib.machinery import ModuleSpec
from pathlib import Path


class NoOpLoader:
    """Loader that uses existing namespace module (prevents __init__.py execution)."""

    def create_module(self, spec):
        """Return existing module from sys.modules if it exists."""
        return sys.modules.get(spec.name)

    def exec_module(self, module):
        """Do nothing - prevents __init__.py execution."""


class AudiometaImportHook:
    """Import hook to prevent audiometa/__init__.py from being executed."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.audiometa_path = project_root / "audiometa"
        self.utils_path = self.audiometa_path / "utils"
        self.loader = NoOpLoader()

    def find_spec(self, name: str, path: object, target: object = None):  # noqa: ARG002
        """Intercept imports of audiometa package and subpackages."""
        if name == "audiometa":
            # Return a spec with a no-op loader to prevent __init__.py execution
            spec = ModuleSpec("audiometa", self.loader, is_package=True)
            spec.submodule_search_locations = [str(self.audiometa_path)]
            return spec
        return None


# Add project root to path so we can import audiometa modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Create minimal namespace packages for audiometa and audiometa.utils FIRST
# This prevents Python from executing audiometa/__init__.py when resolving imports
# We create these before installing the import hook so they're available when needed
audiometa_path = project_root / "audiometa"
utils_path_parent = audiometa_path / "utils"

if "audiometa" not in sys.modules:
    audiometa_module = types.ModuleType("audiometa")
    audiometa_module.__path__ = [str(audiometa_path)]
    sys.modules["audiometa"] = audiometa_module

if "audiometa.utils" not in sys.modules:
    utils_module = types.ModuleType("audiometa.utils")
    utils_module.__path__ = [str(utils_path_parent)]
    sys.modules["audiometa.utils"] = utils_module

if "audiometa.utils.os_dependencies_checker" not in sys.modules:
    checker_module = types.ModuleType("audiometa.utils.os_dependencies_checker")
    sys.modules["audiometa.utils.os_dependencies_checker"] = checker_module

# Install import hook AFTER creating namespace modules
# This prevents audiometa/__init__.py from being executed if something tries to import audiometa
import_hook = AudiometaImportHook(project_root)
sys.meta_path.insert(0, import_hook)

# Import modules directly without triggering audiometa/__init__.py
# This avoids importing mutagen and other dependencies that aren't installed yet
utils_path = utils_path_parent / "os_dependencies_checker"

# Load base module first (needed by other modules)
base_spec = importlib.util.spec_from_file_location(
    "audiometa.utils.os_dependencies_checker.base",
    utils_path / "base.py",
)
base_module = importlib.util.module_from_spec(base_spec)
sys.modules["audiometa.utils.os_dependencies_checker.base"] = base_module
base_spec.loader.exec_module(base_module)  # type: ignore[union-attr]

# Load OS-specific checker modules
macos_spec = importlib.util.spec_from_file_location(
    "audiometa.utils.os_dependencies_checker.macos",
    utils_path / "macos.py",
)
macos_module = importlib.util.module_from_spec(macos_spec)
sys.modules["audiometa.utils.os_dependencies_checker.macos"] = macos_module
macos_spec.loader.exec_module(macos_module)  # type: ignore[union-attr]

ubuntu_spec = importlib.util.spec_from_file_location(
    "audiometa.utils.os_dependencies_checker.ubuntu",
    utils_path / "ubuntu.py",
)
ubuntu_module = importlib.util.module_from_spec(ubuntu_spec)
sys.modules["audiometa.utils.os_dependencies_checker.ubuntu"] = ubuntu_module
ubuntu_spec.loader.exec_module(ubuntu_module)  # type: ignore[union-attr]

windows_spec = importlib.util.spec_from_file_location(
    "audiometa.utils.os_dependencies_checker.windows",
    utils_path / "windows.py",
)
windows_module = importlib.util.module_from_spec(windows_spec)
sys.modules["audiometa.utils.os_dependencies_checker.windows"] = windows_module
windows_spec.loader.exec_module(windows_module)  # type: ignore[union-attr]

# Load config module
config_spec = importlib.util.spec_from_file_location(
    "audiometa.utils.os_dependencies_checker.config",
    utils_path / "config.py",
)
config_module = importlib.util.module_from_spec(config_spec)
sys.modules["audiometa.utils.os_dependencies_checker.config"] = config_module
config_spec.loader.exec_module(config_module)  # type: ignore[union-attr]
load_dependencies_pinned_versions = config_module.load_dependencies_pinned_versions

# Load __init__ module last (which imports the checker classes)
init_spec = importlib.util.spec_from_file_location(
    "audiometa.utils.os_dependencies_checker",
    utils_path / "__init__.py",
)
init_module = importlib.util.module_from_spec(init_spec)
sys.modules["audiometa.utils.os_dependencies_checker"] = init_module
init_spec.loader.exec_module(init_module)  # type: ignore[union-attr]
get_dependencies_checker = init_module.get_dependencies_checker


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
