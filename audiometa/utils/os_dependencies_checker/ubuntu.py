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
