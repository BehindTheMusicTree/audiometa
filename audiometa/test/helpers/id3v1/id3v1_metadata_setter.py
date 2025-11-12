"""ID3v1 metadata setting operations."""

from pathlib import Path
from typing import Any

from ..common.external_tool_runner import run_external_tool


class ID3v1MetadataSetter:
    """Static utility class for ID3v1 metadata setting using external tools."""

    @staticmethod
    def set_genre(file_path: Path, genre_code: str) -> None:
        """Set ID3v1 genre using external id3v2 tool."""
        command = ["id3v2", "--id3v1-only", "--genre", genre_code, str(file_path)]
        run_external_tool(command, "id3v2")

    @staticmethod
    def set_comment(file_path: Path, comment: str) -> None:
        """Set ID3v1 comment using external id3v2 tool."""
        command = ["id3v2", "--id3v1-only", "--comment", comment, str(file_path)]
        run_external_tool(command, "id3v2")

    @staticmethod
    def set_title(file_path: Path, title: str) -> None:
        """Set ID3v1 title using external id3v2 tool."""
        command = ["id3v2", "--id3v1-only", "--song", title, str(file_path)]
        run_external_tool(command, "id3v2")

    @staticmethod
    def set_artist(file_path: Path, artist: str) -> None:
        """Set ID3v1 artist using external id3v2 tool."""
        command = ["id3v2", "--id3v1-only", "--artist", artist, str(file_path)]
        run_external_tool(command, "id3v2")

    @staticmethod
    def set_album(file_path: Path, album: str) -> None:
        """Set ID3v1 album using external id3v2 tool."""
        command = ["id3v2", "--id3v1-only", "--album", album, str(file_path)]
        run_external_tool(command, "id3v2")

    @staticmethod
    def set_max_metadata(file_path: Path) -> None:
        """Set maximum ID3v1 metadata using external script."""
        from pathlib import Path

        from ..common.external_tool_runner import run_script

        scripts_dir = Path(__file__).parent.parent.parent.parent / "test" / "helpers" / "scripts"
        run_script("set-id3v1-max-metadata.sh", file_path, scripts_dir)

    @staticmethod
    def set_metadata(file_path: Path, metadata: dict[str, Any]) -> None:
        """Set ID3v1 metadata using id3v2 tool (id3v2 can also set ID3v1 tags)."""
        # Ensure ID3v1.1 format when track is set
        metadata = metadata.copy()
        if "track" in metadata and "comment" not in metadata:
            metadata["comment"] = " " * 28  # Set comment to 28 spaces to enable ID3v1.1

        cmd = ["id3v2", "--id3v1-only"]

        # Map common metadata keys to id3v2 arguments for ID3v1
        key_mapping = {
            "title": "--song",
            "artist": "--artist",
            "album": "--album",
            "year": "--year",
            "genre": "--genre",
            "comment": "--comment",
            "track": "--track",
        }

        metadata_added = False
        for key, value in metadata.items():
            if key.lower() in key_mapping:
                cmd.extend([key_mapping[key.lower()], str(value)])
                metadata_added = True

        # Only run id3v2 if metadata was actually added
        if metadata_added:
            cmd.append(str(file_path))
            run_external_tool(cmd, "id3v2")
