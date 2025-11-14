#!/usr/bin/env python3
"""Validate system-dependencies.toml versions are accessible.

This hook checks that:
1. ExifTool Windows version can be fetched from ver.txt (if using latest)
2. Or validates that pinned versions are reasonable (not obviously invalid)
"""

import sys
import tomllib
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def validate_exiftool_windows_version(config_path: Path) -> tuple[bool, str]:
    """Validate ExifTool Windows version configuration."""
    try:
        with config_path.open("rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        return False, f"Failed to parse {config_path}: {e}"

    windows_config = config.get("windows", {})
    exiftool_config = windows_config.get("exiftool")

    if not exiftool_config:
        return True, ""  # Not configured, skip

    if isinstance(exiftool_config, dict) and "pinned_version" in exiftool_config:
        pinned_version = exiftool_config["pinned_version"]
    elif isinstance(exiftool_config, str):
        pinned_version = exiftool_config
    else:
        return False, "Invalid exiftool configuration format"

    # If using "latest", verify we can fetch it
    if pinned_version == "latest":
        try:
            with urlopen("https://exiftool.org/ver.txt", timeout=5) as response:
                latest_version = response.read().decode("utf-8").strip()
        except (URLError, HTTPError, TimeoutError) as e:
            return False, f"Cannot fetch latest version from exiftool.org/ver.txt: {e}"
        else:
            return True, f"Latest version available: {latest_version}"

    # For pinned versions, check if version format is reasonable
    # Version should be in format X.Y or X.Y.Z
    version_parts = pinned_version.split(".")
    if len(version_parts) < 2 or len(version_parts) > 3:
        return False, f"Invalid version format: {pinned_version} (expected X.Y or X.Y.Z)"

    try:
        major = int(version_parts[0])
        if major < 10 or major > 20:  # Reasonable range check
            return False, f"Suspicious version number: {pinned_version} (major version out of range)"
    except ValueError:
        return False, f"Invalid version format: {pinned_version} (non-numeric parts)"

    # Check if the download URL is accessible
    download_url = f"https://exiftool.org/exiftool-{pinned_version}_64.zip"
    try:
        import ssl

        # Create unverified context for URL checking (pre-commit hook, not security-critical)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        with urlopen(download_url, timeout=5, context=ssl_context) as response:
            if response.getcode() == 200:
                return True, f"Pinned version {pinned_version} is accessible at {download_url}"
            return False, f"Version {pinned_version} returns HTTP {response.getcode()} at {download_url}"
    except HTTPError as e:
        if e.code == 404:
            return (
                False,
                f"Version {pinned_version} not found (404) at {download_url}. "
                f"Check https://exiftool.org/ for available versions.",
            )
        return False, f"Version {pinned_version} returns HTTP {e.code} at {download_url}"
    except (URLError, TimeoutError) as e:
        # Network error - don't fail pre-commit, but warn
        return True, f"Pinned version format valid: {pinned_version} (could not verify URL accessibility: {e})"


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    config_path = repo_root / "system-dependencies.toml"

    if not config_path.exists():
        sys.stderr.write(f"WARNING: {config_path} not found, skipping validation\n")
        return 0

    is_valid, message = validate_exiftool_windows_version(config_path)
    if not is_valid:
        sys.stderr.write(f"ERROR: System dependency validation failed: {message}\n")
        sys.stderr.write(f"\nFile: {config_path}\n")
        sys.stderr.write("\nPlease check system-dependencies.toml and ensure:\n")
        sys.stderr.write("  - ExifTool Windows version is valid and accessible\n")
        sys.stderr.write("  - If using 'latest', verify https://exiftool.org/ver.txt is accessible\n")
        sys.stderr.write("  - If using pinned version, verify it exists at https://exiftool.org/\n")
        return 1

    if message:
        sys.stdout.write(f"✓ {message}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
