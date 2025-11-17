#!/usr/bin/env python3
"""Load system dependency versions from system-dependencies-*.toml files.

This script reads the TOML configuration files and outputs versions in a format
suitable for shell scripts (bash/PowerShell).

Dependency Categories:
- prod: Production dependencies (ffmpeg, flac, id3v2) - required for library functionality
- test-only: Test-only dependencies (mediainfo, exiftool, bwfmetaedit, libsndfile) - supplementary to prod
- lint: Lint dependencies (PowerShell) - for lint jobs
- all: All dependencies (prod + test-only + lint) - complete test environment

Usage:
    # For bash scripts (test-only dependencies - default):
    eval "$(python3 scripts/load-system-dependency-versions.py bash)"
    eval "$(python3 scripts/load-system-dependency-versions.py bash prod)"
    eval "$(python3 scripts/load-system-dependency-versions.py bash test-only)"
    eval "$(python3 scripts/load-system-dependency-versions.py bash lint)"
    eval "$(python3 scripts/load-system-dependency-versions.py bash all)"

    # For PowerShell scripts:
    python3 scripts/load-system-dependency-versions.py powershell | Out-String | Invoke-Expression
    python3 scripts/load-system-dependency-versions.py powershell prod
    python3 scripts/load-system-dependency-versions.py powershell test-only
    python3 scripts/load-system-dependency-versions.py powershell lint
    python3 scripts/load-system-dependency-versions.py powershell all
"""

import sys
import tomllib
from pathlib import Path


def load_config_file(filename: str) -> dict:
    """Load a TOML configuration file."""
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / filename

    if not config_path.exists():
        sys.stderr.write(f"ERROR: Configuration file not found: {config_path}\n")
        sys.exit(1)

    try:
        with config_path.open("rb") as f:
            return tomllib.load(f)
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to parse {config_path}: {e}\n")
        sys.exit(1)


def load_versions(category: str = "test-only") -> dict:
    """Load versions from system-dependencies-*.toml files based on category.

    Args:
        category: Dependency category - "prod", "test-only", "lint", or "all"

    Returns:
        Combined TOML config dictionary
    """
    config = {}

    if category in ["prod", "all"]:
        prod_config = load_config_file("system-dependencies-prod.toml")
        config.update(prod_config)

    if category in ["test-only", "all"]:
        test_config = load_config_file("system-dependencies-test-only.toml")
        # Merge OS sections
        for os_type in ["ubuntu", "macos", "windows"]:
            if os_type in test_config:
                if os_type not in config:
                    config[os_type] = {}
                config[os_type].update(test_config[os_type])

    if category in ["lint", "all"]:
        lint_config = load_config_file("system-dependencies-lint.toml")
        # Merge OS sections
        for os_type in ["ubuntu", "macos", "windows"]:
            if os_type in lint_config:
                if os_type not in config:
                    config[os_type] = {}
                config[os_type].update(lint_config[os_type])

    return config


def get_version_value(os_config, tool):
    """Extract version from OS config, handling both string and dict values."""
    if tool not in os_config:
        return None

    version_value = os_config[tool]
    if isinstance(version_value, str):
        return version_value  # Return string version as-is
    if isinstance(version_value, dict) and "pinned_version" in version_value:
        return version_value["pinned_version"]
    return None


def get_prod_versions(config, os_type):
    """Get production dependency versions for the specified OS."""
    if os_type not in config:
        return {}

    os_config = config[os_type]
    versions = {}
    for tool in ["ffmpeg", "flac", "id3v2"]:
        version = get_version_value(os_config, tool)
        if version:
            versions[tool] = version
    return versions


def get_test_only_versions(config, os_type):
    """Get test-only dependency versions for the specified OS."""
    if os_type not in config:
        return {}

    os_config = config[os_type]
    versions = {}
    for tool in [
        "mediainfo",
        "bwfmetaedit",
        "exiftool",
        "libimage-exiftool-perl",
        "libsndfile",
        "libsndfile1",
    ]:
        version = get_version_value(os_config, tool)
        if version:
            versions[tool] = version
    return versions


def get_lint_versions(config, os_type):
    """Get lint dependency versions for the specified OS."""
    if os_type not in config:
        return {}

    os_config = config[os_type]
    versions = {}
    for tool in ["powershell"]:
        version = get_version_value(os_config, tool)
        if version:
            versions[tool] = version
    return versions


def output_bash(config, category="test-only"):
    """Output bash-compatible variable assignments.

    Args:
        config: TOML config dictionary
        category: Dependency category - "prod", "test-only", "lint", or "all"
    """
    import platform

    system = platform.system().lower()
    if system == "linux":
        os_type = "ubuntu"
    elif system == "darwin":
        os_type = "macos"
    elif system == "windows":
        os_type = "windows"
    else:
        sys.stderr.write(f"ERROR: Unsupported OS: {system}\n")
        sys.exit(1)

    versions = {}
    if category in ["prod", "all"]:
        versions.update(get_prod_versions(config, os_type))
    if category in ["test-only", "all"]:
        versions.update(get_test_only_versions(config, os_type))
    if category in ["lint", "all"]:
        versions.update(get_lint_versions(config, os_type))

    for tool, version in versions.items():
        var_name = f"PINNED_{tool.upper().replace('-', '_')}"
        sys.stdout.write(f'export {var_name}="{version}"  # {os_type}\n')


def output_powershell(config, category="test-only"):
    """Output PowerShell-compatible variable assignments.

    Args:
        config: TOML config dictionary
        category: Dependency category - "prod", "test-only", "lint", or "all"
    """
    import platform

    system = platform.system().lower()
    if system == "linux":
        os_type = "ubuntu"
    elif system == "darwin":
        os_type = "macos"
    elif system == "windows":
        os_type = "windows"
    else:
        sys.stderr.write(f"ERROR: Unsupported OS: {system}\n")
        sys.exit(1)

    versions = {}
    if category in ["prod", "all"]:
        versions.update(get_prod_versions(config, os_type))
    if category in ["test-only", "all"]:
        versions.update(get_test_only_versions(config, os_type))
    if category in ["lint", "all"]:
        versions.update(get_lint_versions(config, os_type))

    for tool, version in versions.items():
        var_name = f"PINNED_{tool.upper().replace('-', '_')}"
        sys.stdout.write(f'${var_name} = "{version}"  # {os_type}\n')


def main():
    """Main entry point."""
    min_args = 2
    if len(sys.argv) < min_args:
        sys.stderr.write(
            "Usage: python3 load-system-dependency-versions.py [bash|powershell] [prod|test-only|lint|all]\n"
        )
        sys.stderr.write("  Category defaults to 'test-only' if not specified\n")
        sys.exit(1)

    output_format = sys.argv[1].lower()
    min_args_for_category = 3
    category = sys.argv[2].lower() if len(sys.argv) >= min_args_for_category else "test-only"

    if category not in ["prod", "test-only", "lint", "all"]:
        sys.stderr.write(f"ERROR: Unknown category: {category}\n")
        sys.stderr.write("Supported categories: prod, test-only, lint, all\n")
        sys.exit(1)

    config = load_versions(category)

    if output_format == "bash":
        output_bash(config, category)
    elif output_format == "powershell":
        output_powershell(config, category)
    else:
        sys.stderr.write(f"ERROR: Unknown output format: {output_format}\n")
        sys.stderr.write("Supported formats: bash, powershell\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
