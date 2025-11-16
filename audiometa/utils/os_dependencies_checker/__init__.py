"""OS-specific dependency checkers for verifying system dependencies."""

import platform

from audiometa.utils.os_dependencies_checker.base import OsDependenciesChecker
from audiometa.utils.os_dependencies_checker.macos import MacOSDependenciesChecker
from audiometa.utils.os_dependencies_checker.ubuntu import UbuntuDependenciesChecker
from audiometa.utils.os_dependencies_checker.windows import WindowsDependenciesChecker


def get_dependencies_checker() -> OsDependenciesChecker | None:
    """Get the appropriate OS-specific dependencies checker.

    Returns:
        OS-specific checker instance, or None if OS not supported
    """
    system = platform.system().lower()
    if system == "darwin":
        return MacOSDependenciesChecker()
    if system == "linux":
        return UbuntuDependenciesChecker()
    if system == "windows":
        return WindowsDependenciesChecker()
    return None
