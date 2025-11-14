#!/usr/bin/env python3
"""Load system dependency versions from system-dependencies.toml.

This script reads the TOML configuration file and outputs versions in a format
suitable for shell scripts (bash/PowerShell).

Usage:
    # For bash scripts:
    eval "$(python3 scripts/ci/load-system-dependency-versions.py bash)"

    # For PowerShell scripts:
    python3 scripts/ci/load-system-dependency-versions.py powershell | Out-String | Invoke-Expression
"""

import sys
import tomllib
from pathlib import Path


def load_versions():
    """Load versions from system-dependencies.toml."""
    script_dir = Path(__file__).parent
    config_path = script_dir.parent.parent / "system-dependencies.toml"

    if not config_path.exists():
        print(f"ERROR: Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with config_path.open("rb") as f:
            config = tomllib.load(f)
        return config
    except Exception as e:
        print(f"ERROR: Failed to parse {config_path}: {e}", file=sys.stderr)
        sys.exit(1)


def get_version_value(os_config, tool):
    """Extract version from OS config, handling both string and dict values."""
    if tool not in os_config:
        return None

    version_value = os_config[tool]
    if isinstance(version_value, str):
        return version_value  # Return string version as-is
    elif isinstance(version_value, dict) and "pinned_version" in version_value:
        return version_value["pinned_version"]
    return None


def output_bash(config):
    """Output bash-compatible variable assignments."""
    for os_type in ["ubuntu", "macos", "windows"]:
        if os_type not in config:
            continue

        os_config = config[os_type]
        for tool in [
            "ffmpeg",
            "flac",
            "mediainfo",
            "id3v2",
            "bwfmetaedit",
            "exiftool",
            "libimage-exiftool-perl",
            "libsndfile",
            "libsndfile1",
        ]:
            version = get_version_value(os_config, tool)
            if version:
                var_name = f"PINNED_{tool.upper().replace('-', '_')}"
                print(f'export {var_name}="{version}"  # {os_type}')


def output_powershell(config):
    """Output PowerShell-compatible variable assignments."""
    for os_type in ["ubuntu", "macos", "windows"]:
        if os_type not in config:
            continue

        os_config = config[os_type]
        for tool in [
            "ffmpeg",
            "flac",
            "mediainfo",
            "id3v2",
            "bwfmetaedit",
            "exiftool",
            "libimage-exiftool-perl",
            "libsndfile",
            "libsndfile1",
        ]:
            version = get_version_value(os_config, tool)
            if version:
                var_name = f"$PINNED_{tool.upper().replace('-', '_')}"
                print(f'{var_name} = "{version}"  # {os_type}')


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 load-system-dependency-versions.py [bash|powershell]", file=sys.stderr)
        sys.exit(1)

    output_format = sys.argv[1].lower()
    config = load_versions()

    # Filter to current OS
    import platform

    system = platform.system().lower()
    if system == "linux":
        os_type = "ubuntu"
    elif system == "darwin":
        os_type = "macos"
    elif system == "windows":
        os_type = "windows"
    else:
        print(f"ERROR: Unsupported OS: {system}", file=sys.stderr)
        sys.exit(1)

    if os_type not in config:
        print(f"ERROR: No configuration found for {os_type}", file=sys.stderr)
        sys.exit(1)

    os_config = config[os_type]

    if output_format == "bash":
        for tool in [
            "ffmpeg",
            "flac",
            "mediainfo",
            "id3v2",
            "bwfmetaedit",
            "exiftool",
            "libimage-exiftool-perl",
            "libsndfile",
            "libsndfile1",
        ]:
            version = get_version_value(os_config, tool)
            if version is not None:
                var_name = f"PINNED_{tool.upper().replace('-', '_')}"
                print(f'{var_name}="{version}"')
    elif output_format == "powershell":
        for tool in [
            "ffmpeg",
            "flac",
            "mediainfo",
            "id3v2",
            "bwfmetaedit",
            "exiftool",
            "libimage-exiftool-perl",
            "libsndfile",
            "libsndfile1",
        ]:
            version = get_version_value(os_config, tool)
            if version is not None:
                var_name = f"PINNED_{tool.upper().replace('-', '_')}"
                print(f'${var_name} = "{version}"')
    else:
        print(f"ERROR: Unknown output format: {output_format}", file=sys.stderr)
        print("Supported formats: bash, powershell", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
