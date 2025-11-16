"""Windows-specific dependency checker."""

import re
import subprocess
from pathlib import Path

from audiometa.utils.os_dependencies_checker.base import OsDependenciesChecker


class WindowsDependenciesChecker(OsDependenciesChecker):
    """Windows-specific dependency checker."""

    @classmethod
    def get_os_type(cls) -> str:
        return "windows"

    def check_tool_available(self, tool_name: str) -> bool:
        """Check if tool is available in PATH or default Windows locations."""
        # Check default installation paths for manually installed tools
        if tool_name == "bwfmetaedit":
            exe_path = r"C:\Program Files\BWFMetaEdit\bwfmetaedit.exe"
            if Path(exe_path).exists():
                return True
        elif tool_name == "exiftool":
            exe_path = r"C:\Program Files\ExifTool\exiftool.exe"
            if Path(exe_path).exists():
                return True
        elif tool_name == "id3v2":
            wrapper_path = r"C:\Program Files\id3v2-wrapper\id3v2.bat"
            if Path(wrapper_path).exists():
                return True
            try:
                subprocess.run(["wsl", "--version"], capture_output=True, check=False)
            except FileNotFoundError:
                pass
            else:
                return True

        # Check PATH
        try:
            result = subprocess.run(
                [tool_name, "--version" if tool_name != "ffprobe" else "-version"],
                capture_output=True,
                text=True,
                check=False,
            )
            return bool(result.stdout or result.stderr)
        except FileNotFoundError:
            return False

    def get_installed_version(self, package: str, expected_version: str | None = None) -> str | None:  # noqa: ARG002
        """Get installed package version on Windows."""
        # Handle different installation methods
        if package == "id3v2":
            try:
                result = subprocess.run(
                    ["wsl", "id3v2", "--version"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.stdout or result.stderr:
                    output = result.stdout + result.stderr
                    match = re.search(r"(\d+\.\d+\.\d+)", output)
                    if match:
                        return match.group(1)
            except FileNotFoundError:
                pass
            return None

        if package == "bwfmetaedit":
            exe_path = r"C:\Program Files\BWFMetaEdit\bwfmetaedit.exe"
            try:
                if not Path(exe_path).exists():
                    return None

                result = subprocess.run(
                    [exe_path, "--version"],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=10,
                )
                output = result.stdout + result.stderr

                if not output.strip() or result.returncode != 0:
                    result = subprocess.run(
                        [exe_path],
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=10,
                    )
                    output = result.stdout + result.stderr

                if output:
                    patterns = [
                        r"(\d+\.\d+\.\d+)",
                        r"(\d+\.\d+)",
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, output)
                        for match in matches:
                            version = str(match)
                            if re.match(r"^\d+\.\d+", version):
                                return version
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
                pass
            return None

        if package == "exiftool":
            exe_path = r"C:\Program Files\ExifTool\exiftool.exe"
            try:
                result = subprocess.run(
                    [exe_path, "-ver"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.stdout:
                    version = result.stdout.strip()
                    if re.match(r"^\d+\.\d+", version):
                        return version
            except FileNotFoundError:
                pass
            return None

        # For Chocolatey packages
        choco_version = None
        try:
            result = subprocess.run(
                ["choco", "list", "--local-only", package, "--exact"],
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout + result.stderr

            if output.strip():
                pattern = rf"^{re.escape(package)}\s+(\S+)"
                for raw_line in output.split("\n"):
                    line = raw_line.strip()
                    if not line or line.startswith("Chocolatey"):
                        continue

                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        version = match.group(1)
                        if version.startswith(("v", "V")):
                            version = version[1:]
                        if re.match(r"^\d+\.\d+", version):
                            choco_version = version
                            break

                    if "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 2 and parts[0].strip().lower() == package.lower():  # noqa: PLR2004
                            version = parts[1].strip()
                            if version.startswith(("v", "V")):
                                version = version[1:]
                            if re.match(r"^\d+\.\d+", version):
                                choco_version = version
                                break
        except FileNotFoundError:
            pass

        if choco_version:
            return choco_version

        # Fallback: Get version from executable directly (for Chocolatey-installed tools)
        # This handles cases where Chocolatey version detection fails but tool is installed
        tool_name = "ffprobe" if package == "ffmpeg" else package
        try:
            version_flag = "-version" if tool_name == "ffprobe" else "--version"
            result = subprocess.run(
                [tool_name, version_flag],
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout + result.stderr
            if output:
                # Extract version from output (look for patterns like "version 7.1.0" or "7.1.0")
                patterns = [
                    r"version\s+(\d+\.\d+\.\d+)",
                    r"version\s+(\d+\.\d+)",
                    r"(\d+\.\d+\.\d+)",
                    r"(\d+\.\d+)",
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, output, re.IGNORECASE)
                    for match in matches:
                        version = str(match)
                        if re.match(r"^\d+\.\d+", version):
                            return version
        except FileNotFoundError:
            pass

        return None

    @staticmethod
    def _versions_match(version1: str, version2: str) -> bool:
        """Check if two Windows version strings match (handles different precision).

        Handles cases where versions have different precision levels:
        - "7.1.0" matches "7.1" (v2 is prefix of v1)
        - "7.1" matches "7.1.0" (v1 is prefix of v2)
        - "7.1.0" matches "7.1.0" (exact match)

        Args:
            version1: First version string (e.g., "7.1.0")
            version2: Second version string (e.g., "7.1")

        Returns:
            True if versions match, False otherwise
        """
        v1_normalized = OsDependenciesChecker._normalize_version(version1)
        v2_normalized = OsDependenciesChecker._normalize_version(version2)

        # Check exact match
        if v1_normalized == v2_normalized:
            return True

        # Check if one version is a prefix of the other
        # "7.1" should match "7.1.0" (v2 starts with v1 + ".")
        # "7.1.0" should match "7.1" (v1 starts with v2 + ".")
        return v2_normalized.startswith(v1_normalized + ".") or v1_normalized.startswith(v2_normalized + ".")
