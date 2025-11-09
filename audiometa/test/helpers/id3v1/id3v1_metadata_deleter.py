"""ID3v1 metadata deletion operations."""

from pathlib import Path

from ..common.external_tool_runner import ExternalMetadataToolError, run_external_tool


class ID3v1MetadataDeleter:
    """Static utility class for ID3v1 metadata deletion using external tools."""

    @staticmethod
    def delete_tag(file_path: Path, tag_name: str) -> None:
        try:
            command = ["id3v2", "--id3v1-only", "--delete", tag_name, str(file_path)]
            run_external_tool(command, "id3v2")
        except ExternalMetadataToolError:
            pass

    @staticmethod
    def delete_comment(file_path: Path) -> None:
        ID3v1MetadataDeleter.delete_tag(file_path, "COMM")

    @staticmethod
    def delete_title(file_path: Path) -> None:
        ID3v1MetadataDeleter.delete_tag(file_path, "TIT2")

    @staticmethod
    def delete_artist(file_path: Path) -> None:
        ID3v1MetadataDeleter.delete_tag(file_path, "TPE1")

    @staticmethod
    def delete_album(file_path: Path) -> None:
        ID3v1MetadataDeleter.delete_tag(file_path, "TALB")

    @staticmethod
    def delete_genre(file_path: Path) -> None:
        ID3v1MetadataDeleter.delete_tag(file_path, "TCON")
