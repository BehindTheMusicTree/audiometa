"""Base class for OS-specific dependency checkers."""

from abc import ABC, abstractmethod


class OsDependenciesChecker(ABC):
    """Base class for OS-specific dependency checkers."""

    @classmethod
    @abstractmethod
    def get_os_type(cls) -> str:
        """Get OS type identifier."""

    @abstractmethod
    def check_tool_available(self, tool_name: str) -> bool:
        """Check if a tool is available (in PATH or default locations).

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if tool is available, False otherwise
        """

    @abstractmethod
    def get_installed_version(self, package: str, expected_version: str | None = None) -> str | None:
        """Get installed version of a package.

        Args:
            package: Package name
            expected_version: Optional expected/pinned version

        Returns:
            Installed version string, or None if not found
        """

    @staticmethod
    def _normalize_version(version: str) -> str:
        """Normalize version string by removing revision suffix.

        Args:
            version: Version string (e.g., "7.1_4" or "1.5.0")

        Returns:
            Normalized version without revision suffix
        """
        return version.split("_")[0]

    @staticmethod
    def _versions_match(version1: str, version2: str) -> bool:
        """Check if two version strings match (handles different precision).

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            True if versions match, False otherwise
        """
        v1_normalized = OsDependenciesChecker._normalize_version(version1)
        v2_normalized = OsDependenciesChecker._normalize_version(version2)
        return v1_normalized == v2_normalized or v2_normalized.startswith(v1_normalized + ".")
