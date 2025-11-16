"""Vorbis metadata header verification and information utilities."""

import subprocess
from pathlib import Path

from audiometa.utils.tool_path_resolver import get_tool_path

from ..common.external_tool_runner import run_external_tool


class VorbisHeaderVerifier:
    """Utilities for verifying Vorbis metadata headers and retrieving metadata information from audio files."""

    @staticmethod
    def has_vorbis_comments(file_path: Path) -> bool:
        """Check if file has Vorbis comments using metaflac."""
        try:
            result = subprocess.run(
                [get_tool_path("metaflac"), "--list", str(file_path)], capture_output=True, text=True, check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
        else:
            return "VORBIS_COMMENT" in result.stdout

    @staticmethod
    def get_metadata_info(file_path: Path) -> str:
        """Get metadata info using metaflac --list command."""
        command = [get_tool_path("metaflac"), "--list", str(file_path)]
        result = run_external_tool(command, "metaflac")
        return result.stdout
