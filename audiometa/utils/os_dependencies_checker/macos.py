"""MacOS-specific dependency checker using Homebrew."""

import re
import subprocess
from pathlib import Path

from audiometa.utils.os_dependencies_checker.base import OsDependenciesChecker


class MacOSDependenciesChecker(OsDependenciesChecker):
    """MacOS-specific dependency checker using Homebrew."""

    @classmethod
    def get_os_type(cls) -> str:
        return "macos"

    def _get_brew_prefix(self) -> str | None:
        """Get Homebrew prefix path."""
        try:
            result = subprocess.run(
                ["brew", "--prefix"],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout:
                return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def _extract_version_from_output(self, output: str, tool_name: str) -> str | None:
        """Extract version number from tool output."""
        if tool_name in ["flac", "metaflac"]:
            match = re.search(r"(\d+\.\d+\.\d+)", output)
        elif tool_name == "mediainfo":
            match = re.search(r"(\d+\.\d+(?:\.\d+)?)", output)
        elif tool_name in ["id3v2", "bwfmetaedit"]:
            match = re.search(r"(\d+\.\d+\.\d+)", output)
        elif tool_name == "exiftool":
            match = re.search(r"(\d+\.\d+(?:\.\d+)?)", output)
        else:
            match = re.search(r"(\d+\.\d+\.\d+)", output)

        return match.group(1) if match else None

    def check_tool_available(self, tool_name: str) -> bool:
        """Check if tool is available in PATH or Homebrew locations."""
        brew_prefix = self._get_brew_prefix()
        if brew_prefix:
            tool_paths = [
                f"{brew_prefix}/opt/{tool_name}/bin/{tool_name}",
                f"{brew_prefix}/bin/{tool_name}",
            ]
            # Special handling for ffmpeg/ffprobe (keg-only packages)
            if tool_name in ["ffmpeg", "ffprobe"]:
                for version in ["7", "6", "5"]:
                    tool_paths.insert(0, f"{brew_prefix}/opt/ffmpeg@{version}/bin/{tool_name}")

            for tool_path in tool_paths:
                if Path(tool_path).exists() and Path(tool_path).is_file():
                    try:
                        # exiftool uses -ver, not --version
                        if tool_name == "exiftool":
                            version_flag = "-ver"
                        elif tool_name == "ffprobe":
                            version_flag = "-version"
                        else:
                            version_flag = "--version"
                        result = subprocess.run(
                            [tool_path, version_flag],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        if result.stdout or result.stderr:
                            return True
                    except Exception:
                        continue

        # Fallback to PATH check
        try:
            # exiftool uses -ver, not --version
            if tool_name == "exiftool":
                version_flag = "-ver"
            elif tool_name == "ffprobe":
                version_flag = "-version"
            else:
                version_flag = "--version"
            result = subprocess.run(
                [tool_name, version_flag],
                capture_output=True,
                text=True,
                check=False,
            )
            return bool(result.stdout or result.stderr)
        except FileNotFoundError:
            return False

    def _get_ffmpeg_version(self) -> str | None:
        """Get ffmpeg version (special handling for keg-only package)."""
        ffprobe_paths = ["ffprobe"]
        brew_prefix = self._get_brew_prefix()
        if brew_prefix:
            for version in ["7", "6", "5"]:
                ffprobe_paths.append(f"{brew_prefix}/opt/ffmpeg@{version}/bin/ffprobe")

        for ffprobe_path in ffprobe_paths:
            try:
                result = subprocess.run(
                    [ffprobe_path, "-version"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.stdout or result.stderr:
                    output = result.stdout + result.stderr
                    match = re.search(r"version\s+(\d+(?:\.\d+)*)", output)
                    if match:
                        return match.group(1)
            except FileNotFoundError:
                continue
        return None

    def _get_running_version_from_executable(self, package: str, tool_name: str) -> str | None:
        """Get version from tool executable."""
        tool_paths = [tool_name]
        brew_prefix = self._get_brew_prefix()
        if brew_prefix:
            tool_paths.extend(
                [
                    f"{brew_prefix}/opt/{package}/bin/{tool_name}",
                    f"{brew_prefix}/bin/{tool_name}",
                ]
            )

        for tool_path in tool_paths:
            try:
                # exiftool uses -ver, not --version
                if tool_name == "exiftool":
                    version_flag = "-ver"
                elif tool_name == "ffprobe":
                    version_flag = "-version"
                else:
                    version_flag = "--version"
                result = subprocess.run(
                    [tool_path, version_flag],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.stdout or result.stderr:
                    output = result.stdout + result.stderr
                    version = self._extract_version_from_output(output, tool_name)
                    if version:
                        return version
            except FileNotFoundError:
                continue
        return None

    def _get_installed_versions_from_brew(self, package: str) -> list[str] | None:
        """Get list of installed versions from Homebrew."""
        try:
            result = subprocess.run(
                ["brew", "list", "--versions", package],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout:
                parts = result.stdout.strip().split()
                if len(parts) > 1:
                    return parts[1:]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def _verify_pinned_version_installed(self, installed_versions: list[str], expected_version: str) -> bool:
        """Verify that pinned version is in the installed versions list."""
        expected_normalized = self._normalize_version(expected_version)
        for version in installed_versions:
            version_normalized = self._normalize_version(version)
            if self._versions_match(expected_normalized, version_normalized):
                return True
        return False

    def _find_pinned_version_in_list(self, installed_versions: list[str], expected_version: str) -> str | None:
        """Find and return the pinned version from installed versions list."""
        expected_normalized = self._normalize_version(expected_version)
        for version in installed_versions:
            version_normalized = self._normalize_version(version)
            if self._versions_match(expected_normalized, version_normalized):
                return version_normalized
        return None

    def get_installed_version(self, package: str, expected_version: str | None = None) -> str | None:
        """Get installed package version on macOS."""
        # Special handling for ffmpeg
        if package == "ffmpeg":
            return self._get_ffmpeg_version()

        # Map package name to tool executable name
        tool_name = package
        if package == "media-info":
            tool_name = "mediainfo"

        # Get running version from executable
        running_version = self._get_running_version_from_executable(package, tool_name)

        # Verify pinned version is installed
        installed_versions = self._get_installed_versions_from_brew(package)
        if installed_versions is None:
            return running_version

        # If expected version is provided, check if running version or Homebrew version matches
        if expected_version:
            # Accept running version if it matches the pinned version
            # This handles cases where tool is installed manually or from another source
            if running_version and self._versions_match(expected_version, running_version):
                return running_version

            # If running version doesn't match, check if Homebrew has the pinned version
            if installed_versions:
                pinned_version = self._find_pinned_version_in_list(installed_versions, expected_version)
                if pinned_version:
                    # Homebrew has the pinned version, but running version doesn't match
                    # Return None to indicate mismatch (running version should match pinned version)
                    return None

            # Pinned version not found in Homebrew and running version doesn't match
            return None

        # If expected version not provided, return running version or first installed version
        if running_version:
            return running_version
        return self._normalize_version(installed_versions[0])
