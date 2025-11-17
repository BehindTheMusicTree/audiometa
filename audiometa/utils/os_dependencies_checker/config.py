"""Configuration loading for OS-specific dependency checkers."""

import tomllib
from pathlib import Path


def _load_config_file(project_root: Path, filename: str) -> dict | None:
    """Load a TOML configuration file."""
    config_path = project_root / filename
    if not config_path.exists():
        return None

    try:
        with config_path.open("rb") as f:
            return tomllib.load(f)
    except Exception:
        return None


def load_dependencies_pinned_versions() -> dict[str, dict[str, str]] | None:
    """Load pinned versions from system-dependencies-prod.toml and system-dependencies-test-only.toml.

    Returns:
        Dictionary mapping tool names to OS-specific versions, or None if config not found
    """
    # Try to find config files relative to this file
    # This file is in audiometa/utils/os_dependencies_checker/, so go up to project root
    project_root = Path(__file__).parent.parent.parent.parent

    # Load prod and test configs
    prod_config = _load_config_file(project_root, "system-dependencies-prod.toml")
    test_config = _load_config_file(project_root, "system-dependencies-test-only.toml")

    if not prod_config and not test_config:
        return None

    try:
        # Merge configs (test can override prod if needed, though they shouldn't overlap)
        config = {}
        if prod_config:
            config.update(prod_config)
        if test_config:
            # Merge OS sections
            for os_type in ["ubuntu", "macos", "windows"]:
                if os_type in test_config:
                    if os_type not in config:
                        config[os_type] = {}
                    config[os_type].update(test_config[os_type])

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
