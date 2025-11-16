"""Utility to resolve paths to pinned versions of external tools."""

import platform
import subprocess
from pathlib import Path

from audiometa.utils.os_dependencies_checker.config import load_dependencies_pinned_versions


def _get_os_type() -> str | None:
    """Detect OS type."""
    system = platform.system().lower()
    if system == "linux":
        return "ubuntu"
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    return None


def get_tool_path(tool_name: str) -> str:
    """Get the path to the pinned version of a tool, or fallback to tool name.

    This function resolves the absolute path to the pinned version's executable
    if available, ensuring the correct version is used. Falls back to the tool
    name if pinned version path cannot be resolved (relies on PATH).

    Args:
        tool_name: Name of the tool (e.g., "flac", "ffprobe", "metaflac")

    Returns:
        Absolute path to pinned version executable, or tool name if not found
    """
    pinned_versions = load_dependencies_pinned_versions()
    if not pinned_versions:
        return tool_name

    os_type = _get_os_type()
    if not os_type:
        return tool_name

    # Map tool names to Homebrew package names
    brew_package_map = {
        "ffmpeg": "ffmpeg",
        "ffprobe": "ffmpeg",  # ffprobe comes from ffmpeg package
        "flac": "flac",
        "metaflac": "flac",  # metaflac comes from flac package
        "mediainfo": "media-info",
        "id3v2": "id3v2",
        "bwfmetaedit": "bwfmetaedit",
        "exiftool": "exiftool",
    }

    brew_package = brew_package_map.get(tool_name)
    if not brew_package:
        return tool_name

    # Get pinned version for this OS
    if brew_package not in pinned_versions:
        return tool_name

    versions = pinned_versions[brew_package]
    pinned_version = versions.get(os_type)
    if not pinned_version:
        return tool_name

    # Resolve path based on OS
    if os_type == "macos":
        try:
            brew_prefix_result = subprocess.run(
                ["brew", "--prefix"],
                capture_output=True,
                text=True,
                check=True,
            )
            if brew_prefix_result.stdout:
                brew_prefix = brew_prefix_result.stdout.strip()

                # Special handling for ffmpeg/ffprobe (keg-only, versioned)
                if brew_package == "ffmpeg":
                    # ffmpeg@7 is keg-only, check versioned path
                    tool_path = Path(brew_prefix) / "opt" / f"ffmpeg@{pinned_version}" / "bin" / tool_name
                    if tool_path.exists() and tool_path.is_file():
                        return str(tool_path)

                # For other tools, check Cellar (exact version) and opt (symlink)
                # Check Cellar first (exact version path)
                cellar_path = Path(brew_prefix) / "Cellar" / brew_package / pinned_version / "bin" / tool_name
                if cellar_path.exists() and cellar_path.is_file():
                    return str(cellar_path)

                # Check opt (symlink, usually points to latest)
                opt_path = Path(brew_prefix) / "opt" / brew_package / "bin" / tool_name
                if opt_path.exists() and opt_path.is_file():
                    # Verify it's the pinned version
                    try:
                        result = subprocess.run(
                            [str(opt_path), "--version" if tool_name != "ffprobe" else "-version"],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        output = result.stdout + result.stderr
                        # Check if version matches pinned version
                        import re

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

                        if match:
                            running_version = match.group(1)
                            # Normalize for comparison
                            pinned_normalized = pinned_version.split("_")[0]
                            running_normalized = running_version.split("_")[0]
                            if running_normalized == pinned_normalized or running_normalized.startswith(
                                pinned_normalized + "."
                            ):
                                return str(opt_path)
                    except Exception:
                        pass

        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Fallback: return tool name (will use PATH)
    return tool_name
