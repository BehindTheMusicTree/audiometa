"""Configuration loading for OS-specific dependency checkers."""

import tomllib
from pathlib import Path


def load_dependencies_pinned_versions() -> dict[str, dict[str, str]] | None:
    """Load pinned versions from system-dependencies.toml.

    Returns:
        Dictionary mapping tool names to OS-specific versions, or None if config not found
    """
    # Try to find system-dependencies.toml relative to this file
    # This file is in audiometa/utils/os_dependencies_checker/, so go up to project root
    config_path = Path(__file__).parent.parent.parent.parent / "system-dependencies.toml"

    if not config_path.exists():
        return None

    try:
        with config_path.open("rb") as f:
            config = tomllib.load(f)

        pinned_versions: dict[str, dict[str, str]] = {}

        # Extract versions for each OS
        for os_type in ["ubuntu", "macos", "windows"]:
            if os_type not in config:
                continue

            os_config = config[os_type]
            for tool in ["ffmpeg", "flac", "mediainfo", "id3v2", "bwfmetaedit", "exiftool"]:
                if tool not in os_config:
                    continue

                version_value = os_config[tool]
                # Handle both string values and dict values (for bwfmetaedit, exiftool on Windows)
                if isinstance(version_value, str):
                    version = version_value
                elif isinstance(version_value, dict) and "pinned_version" in version_value:
                    version = version_value["pinned_version"]
                else:
                    continue

                if tool not in pinned_versions:
                    pinned_versions[tool] = {}
                pinned_versions[tool][os_type] = version
    except Exception:
        return None
    else:
        return pinned_versions
