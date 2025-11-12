"""RIFF metadata deletion operations."""

from pathlib import Path

from ..common.external_tool_runner import run_external_tool


class RIFFMetadataDeleter:
    """Static utility class for RIFF metadata deletion using external bwfmetaedit tool."""

    @staticmethod
    def remove_chunk(file_path: Path, chunk_name: str) -> None:
        """Remove a specific RIFF chunk."""
        try:
            command = ["bwfmetaedit", f"--remove-chunks=INFO/{chunk_name}", str(file_path)]
            run_external_tool(command, "bwfmetaedit")
        except Exception:
            # Ignore if chunk doesn't exist
            pass

    @staticmethod
    def delete_comment(file_path: Path) -> None:
        """Delete RIFF comment using bwfmetaedit tool."""
        RIFFMetadataDeleter.remove_chunk(file_path, "ICMT")

    @staticmethod
    def delete_title(file_path: Path) -> None:
        """Delete RIFF title using bwfmetaedit tool."""
        RIFFMetadataDeleter.remove_chunk(file_path, "INAM")

    @staticmethod
    def delete_artist(file_path: Path) -> None:
        """Delete RIFF artist using bwfmetaedit tool."""
        RIFFMetadataDeleter.remove_chunk(file_path, "IART")

    @staticmethod
    def delete_album(file_path: Path) -> None:
        """Delete RIFF album using bwfmetaedit tool."""
        RIFFMetadataDeleter.remove_chunk(file_path, "IPRD")

    @staticmethod
    def delete_genre(file_path: Path) -> None:
        """Delete RIFF genre using bwfmetaedit tool."""
        RIFFMetadataDeleter.remove_chunk(file_path, "IGNR")

    @staticmethod
    def delete_lyrics(file_path: Path) -> None:
        """Delete RIFF lyrics using bwfmetaedit tool."""
        RIFFMetadataDeleter.remove_chunk(file_path, "ILYT")

    @staticmethod
    def delete_language(file_path: Path) -> None:
        """Delete RIFF language using bwfmetaedit tool."""
        RIFFMetadataDeleter.remove_chunk(file_path, "ILNG")

    # RIFF doesn't support BPM field - use inherited pass implementation
