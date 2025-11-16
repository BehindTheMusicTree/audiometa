"""Ubuntu-specific dependency checker using dpkg."""

import subprocess

from audiometa.utils.os_dependencies_checker.base import OsDependenciesChecker


class UbuntuDependenciesChecker(OsDependenciesChecker):
    """Ubuntu-specific dependency checker using dpkg."""

    @classmethod
    def get_os_type(cls) -> str:
        return "ubuntu"

    def check_tool_available(self, tool_name: str) -> bool:
        """Check if tool is available in PATH."""
        try:
            result = subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            return bool(result.stdout or result.stderr)
        except FileNotFoundError:
            return False

    def get_installed_version(self, package: str, expected_version: str | None = None) -> str | None:  # noqa: ARG002
        """Get installed package version on Ubuntu."""
        try:
            result = subprocess.run(["dpkg", "-l"], capture_output=True, text=True, check=True)
            for line in result.stdout.split("\n"):
                if line.startswith("ii") and package in line:
                    parts = line.split()
                    if len(parts) >= 3:  # noqa: PLR2004
                        return parts[2]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    @staticmethod
    def _versions_match(version1: str, version2: str) -> bool:
        """Check if two Ubuntu/Debian package version strings match.

        Handles Debian package version format: upstream-version-debian-revision
        Compares the upstream version part (before the first '-') for compatibility.

        Args:
            version1: First version string (e.g., "24.01.1-1build2" or "25.04.1")
            version2: Second version string (e.g., "24.01+dfsg-1build2" or "25.04.1-1")

        Returns:
            True if upstream versions match, False otherwise
        """
        # Extract upstream version (part before first '-')
        # Handle both formats: "24.01.1-1build2" -> "24.01.1" and "25.04.1" -> "25.04.1"
        v1_upstream = version1.split("-")[0]
        v2_upstream = version2.split("-")[0]

        # Normalize versions (remove revision suffix like _4)
        v1_normalized = OsDependenciesChecker._normalize_version(v1_upstream)
        v2_normalized = OsDependenciesChecker._normalize_version(v2_upstream)

        # Check if versions match exactly or if one is a prefix of the other
        return v1_normalized == v2_normalized or v2_normalized.startswith(v1_normalized + ".")
