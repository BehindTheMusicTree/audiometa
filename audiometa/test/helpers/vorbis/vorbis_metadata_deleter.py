"""Vorbis metadata deletion operations."""

import contextlib
from pathlib import Path

from ..common.external_tool_runner import run_external_tool


class VorbisMetadataDeleter:
    """Static utility class for Vorbis metadata deletion using external metaflac tool."""

    @staticmethod
    def delete_tag(file_path: Path, tag_name: str) -> None:
        """Delete a specific Vorbis comment tag using metaflac tool."""
        command = ["metaflac", "--remove-tag", tag_name, str(file_path)]
        with contextlib.suppress(Exception):
            run_external_tool(command, "metaflac")

    @staticmethod
    def delete_comment(file_path: Path) -> None:
        VorbisMetadataDeleter.delete_tag(file_path, "COMMENT")

    @staticmethod
    def delete_title(file_path: Path) -> None:
        VorbisMetadataDeleter.delete_tag(file_path, "TITLE")

    @staticmethod
    def delete_artist(file_path: Path) -> None:
        VorbisMetadataDeleter.delete_tag(file_path, "ARTIST")

    @staticmethod
    def delete_album(file_path: Path) -> None:
        VorbisMetadataDeleter.delete_tag(file_path, "ALBUM")

    @staticmethod
    def delete_genre(file_path: Path) -> None:
        VorbisMetadataDeleter.delete_tag(file_path, "GENRE")

    @staticmethod
    def delete_lyrics(file_path: Path) -> None:
        VorbisMetadataDeleter.delete_tag(file_path, "UNSYNCHRONIZED_LYRICS")

    @staticmethod
    def delete_language(file_path: Path) -> None:
        VorbisMetadataDeleter.delete_tag(file_path, "LANGUAGE")

    @staticmethod
    def delete_bpm(file_path: Path) -> None:
        VorbisMetadataDeleter.delete_tag(file_path, "BPM")
