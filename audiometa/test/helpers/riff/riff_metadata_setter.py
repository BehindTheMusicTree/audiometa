"""RIFF metadata setting operations."""

from pathlib import Path
from typing import Any

from ..common.external_tool_runner import ExternalMetadataToolError, run_external_tool


class RIFFMetadataSetter:
    """Static utility class for RIFF metadata setting using external tools."""

    @staticmethod
    def set_metadata(file_path: Path, metadata: dict[str, Any]) -> None:
        """Set WAV metadata using bwfmetaedit tool."""
        cmd = ["bwfmetaedit"]

        # Map common metadata keys to bwfmetaedit arguments
        key_mapping = {
            "title": "--INAM",
            "artist": "--IART",
            "album": "--IPRD",
            "genre": "--IGNR",
            "date": "--ICRD",
            "comment": "--ICMT",
            "track": "--ITRK",
            "bpm": "--TBPM",
            "composer": "--ICMP",
            "lyrics": "--ILYR",
            "language": "--ILNG",
            "album_artist": "--IAAR",
            "rating": "--IRTD",
        }

        metadata_added = False
        for key, value in metadata.items():
            if key.lower() in key_mapping:
                if key.lower() == "bpm":
                    from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

                    ManualRIFFMetadataCreator.create_bpm_field(file_path, str(value))
                    metadata_added = True
                else:
                    cmd.extend([f"{key_mapping[key.lower()]}={value}"])
                    metadata_added = True

        # Only run bwfmetaedit if metadata was actually added
        if metadata_added:
            cmd.append(str(file_path))
            run_external_tool(cmd, "bwfmetaedit")

    @staticmethod
    def set_comment(file_path: Path, comment: str) -> None:
        command = ["bwfmetaedit", f"--ICMT={comment}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_title(file_path: Path, title: str) -> None:
        command = ["bwfmetaedit", f"--INAM={title}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_multiple_titles(file_path: Path, titles: list[str], in_separate_frames: bool = False):
        """Set multiple titles, optionally in separate INAM frames."""
        if in_separate_frames:
            from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

            ManualRIFFMetadataCreator.create_multiple_title_fields(file_path, titles)
        # For now, just set the first title
        elif titles:
            command = ["bwfmetaedit", f"--INAM={titles[0]}", str(file_path)]
            run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_artist(file_path: Path, artist: str) -> None:
        command = ["bwfmetaedit", f"--IART={artist}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_album(file_path: Path, album: str) -> None:
        command = ["bwfmetaedit", f"--IPRD={album}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_genres(file_path: Path, genres: list[str]) -> None:
        command = ["bwfmetaedit", f"--IGNR={','.join(genres)}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_genre_text(file_path: Path, genre_text: str) -> None:
        """Set RIFF genre using external exiftool or bwfmetaedit tool."""
        try:
            # Try exiftool first
            RIFFMetadataSetter.set_riff_genre(file_path, genre_text)
        except ExternalMetadataToolError:
            try:
                # Fallback to bwfmetaedit - split genre_text by semicolon and strip whitespace
                genres = [genre.strip() for genre in genre_text.split(";") if genre.strip()]
                RIFFMetadataSetter.set_genres(file_path, genres)
            except ExternalMetadataToolError as e:
                msg = f"Failed to set RIFF genre: {e}"
                raise RuntimeError(msg) from e

    @staticmethod
    def set_lyrics(file_path: Path, lyrics: str) -> None:
        from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

        ManualRIFFMetadataCreator.create_lyrics_field(file_path, lyrics)

    @staticmethod
    def set_language(file_path: Path, language: str) -> None:
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        try:
            command = [
                "ffmpeg",
                "-i",
                str(file_path),
                "-c",
                "copy",
                "-metadata",
                f"language={language}",
                "-y",
                str(tmp_path),
            ]
            run_external_tool(command, "ffmpeg")
            tmp_path.replace(file_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    @staticmethod
    def set_max_metadata(file_path: Path) -> None:
        from pathlib import Path

        from ..common.external_tool_runner import run_script

        scripts_dir = Path(__file__).parent.parent.parent.parent / "test" / "helpers" / "scripts"
        run_script("set-riff-max-metadata.sh", file_path, scripts_dir)

    @staticmethod
    def set_riff_genre(file_path: Path, genre: str) -> None:
        command = ["exiftool", "-overwrite_original", f"-Genre={genre}", str(file_path)]
        run_external_tool(command, "exiftool")

    @staticmethod
    def set_artists(file_path: Path, artists: list[str], in_separate_frames: bool = False):
        """Set multiple artists, optionally in separate IART frames."""
        if in_separate_frames:
            from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

            ManualRIFFMetadataCreator.create_multiple_artist_fields(file_path, artists)
        # For testing multiple instances, we'd need to use a more sophisticated approach
        # For now, just set the first artist
        elif artists:
            command = ["bwfmetaedit", f"--IART={artists[0]}", str(file_path)]
            run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_multiple_genres(file_path: Path, genres: list[str], in_separate_frames: bool = False):
        """Set multiple genres, optionally in separate IGNR frames."""
        if in_separate_frames:
            from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

            ManualRIFFMetadataCreator.create_multiple_genre_fields(file_path, genres)
        # For now, just set the first genre
        elif genres:
            command = ["bwfmetaedit", f"--IGNR={genres[0]}", str(file_path)]
            run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_multiple_composers(file_path: Path, composers: list[str], in_separate_frames: bool = False):
        """Set multiple composers, optionally in separate ICMP frames."""
        if in_separate_frames:
            from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

            ManualRIFFMetadataCreator.create_multiple_composer_fields(file_path, composers)
        # For now, just set the first composer
        elif composers:
            command = ["bwfmetaedit", f"--ICMP={composers[0]}", str(file_path)]
            run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_multiple_album_artists(file_path: Path, album_artists: list[str], _in_separate_frames: bool = False):
        """Set multiple album artists, optionally in separate IAAR frames."""
        # IAAR is not a standard RIFF INFO chunk field, so external tools don't support it.
        # Use the manual metadata creator which can create non-standard RIFF fields.
        from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

        ManualRIFFMetadataCreator.create_multiple_album_artist_fields(file_path, album_artists)

    @staticmethod
    def set_release_date(file_path: Path, release_date: str) -> None:
        command = ["bwfmetaedit", f"--ICRD={release_date}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")
