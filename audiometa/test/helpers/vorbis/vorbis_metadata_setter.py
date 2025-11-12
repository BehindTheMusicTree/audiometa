"""Vorbis metadata setting operations."""

from pathlib import Path
from typing import Any

from mutagen.flac import FLAC

from ..common.external_tool_runner import run_external_tool


class VorbisMetadataSetter:
    """Static utility class for Vorbis metadata setting using external tools."""

    @staticmethod
    def set_multiple_tags(
        file_path: Path, tag_name: str, values: list[str], removing_existing=True, key_lower_case=False
    ) -> None:
        """Set multiple Vorbis comment tags with the same name."""

        if key_lower_case:
            tag_name = tag_name.lower()

        if removing_existing:
            try:
                command = ["metaflac", "--remove-tag", tag_name, str(file_path)]
                run_external_tool(command, "metaflac")
            except Exception:
                # Ignore if tags don't exist
                pass

        # Add each value as a separate tag
        for value in values:
            command = ["metaflac", "--set-tag", f"{tag_name}={value}", str(file_path)]
            run_external_tool(command, "metaflac")

    @staticmethod
    def set_metadata(file_path: Path, metadata: dict[str, Any]) -> None:
        """Set FLAC metadata using metaflac tool."""
        cmd = ["metaflac"]

        # Map common metadata keys to metaflac arguments
        key_mapping = {
            "title": "TITLE",
            "artist": "ARTIST",
            "album": "ALBUM",
            "date": "DATE",
            "genre": "GENRE",
            "comment": "COMMENT",
            "track_number": "TRACKNUMBER",
            "bpm": "BPM",
            "composer": "COMPOSER",
            "copyright": "COPYRIGHT",
            "lyrics": "LYRICS",
            "language": "LANGUAGE",
            "rating": "RATING",
            "album_artist": "ALBUMARTIST",
            "mood": "MOOD",
            "key": "KEY",
            "encoder": "ENCODER",
            "url": "URL",
            "isrc": "ISRC",
            "publisher": "PUBLISHER",
        }

        metadata_added = False
        for key, value in metadata.items():
            if key.lower() in key_mapping:
                cmd.extend([f"--set-tag={key_mapping[key.lower()]}={value}"])
                metadata_added = True

        # Only run metaflac if metadata was actually added
        if metadata_added:
            cmd.append(str(file_path))
            run_external_tool(cmd, "metaflac")

    @staticmethod
    def set_genre(file_path: Path, genre_text: str) -> None:
        command = ["metaflac", "--set-tag", f"GENRE={genre_text}", str(file_path)]
        run_external_tool(command, "metaflac")

    @staticmethod
    def set_comment(file_path: Path, comment: str) -> None:
        command = ["metaflac", "--set-tag", f"COMMENT={comment}", str(file_path)]
        run_external_tool(command, "metaflac")

    @staticmethod
    def add_title(file_path: Path, title: str, key_lower_case=False) -> None:
        if key_lower_case:
            command = ["metaflac", "--set-tag", f"title={title}", str(file_path)]
        else:
            command = ["metaflac", "--set-tag", f"TITLE={title}", str(file_path)]
        run_external_tool(command, "metaflac")

    @staticmethod
    def set_artist(file_path: Path, artist: str) -> None:
        command = ["metaflac", "--set-tag", f"ARTIST={artist}", str(file_path)]
        run_external_tool(command, "metaflac")

    @staticmethod
    def set_album(file_path: Path, album: str) -> None:
        command = ["metaflac", "--set-tag", f"ALBUM={album}", str(file_path)]
        run_external_tool(command, "metaflac")

    @staticmethod
    def set_lyrics(file_path: Path, lyrics: str) -> None:
        command = ["metaflac", "--set-tag", f"LYRICS={lyrics}", str(file_path)]
        run_external_tool(command, "metaflac")

    @staticmethod
    def set_language(file_path: Path, language: str) -> None:
        command = ["metaflac", "--set-tag", f"LANGUAGE={language}", str(file_path)]
        run_external_tool(command, "metaflac")

    @staticmethod
    def set_bpm(file_path: Path, bpm: int) -> None:
        command = ["metaflac", "--set-tag", f"BPM={bpm}", str(file_path)]
        run_external_tool(command, "metaflac")

    @staticmethod
    def set_release_date(file_path: Path, date_str: str) -> None:
        """Set Vorbis release date using DATE tag."""
        command = ["metaflac", "--set-tag", f"DATE={date_str}", str(file_path)]
        run_external_tool(command, "metaflac")

    @staticmethod
    def set_max_metadata(file_path: Path) -> None:
        from pathlib import Path

        from ..common.external_tool_runner import run_script

        scripts_dir = Path(__file__).parent.parent.parent.parent / "test" / "helpers" / "scripts"
        run_script("set-vorbis-max-metadata.sh", file_path, scripts_dir)

    @staticmethod
    def set_artists(
        file_path: Path, artists: list[str], removing_existing=True, key_lower_case=False, in_single_entry=False
    ) -> None:
        """Set multiple Vorbis artists using mutagen."""
        audio = FLAC(str(file_path))
        key = "artist" if key_lower_case else "ARTIST"
        if removing_existing:
            existing = []
        else:
            existing = audio.get(key, [])
            if isinstance(existing, str):
                existing = [existing]
        if in_single_entry:
            value = "\x00".join(artists)
            existing.append(value)
        else:
            existing.extend(artists)
        audio[key] = existing
        audio.save()

    @staticmethod
    def set_album_artists(file_path: Path, album_artists: list[str]):
        """Set multiple Vorbis album artists using external metaflac tool."""
        VorbisMetadataSetter.set_multiple_tags(file_path, "ALBUMARTIST", album_artists)

    @staticmethod
    def set_composers(file_path: Path, composers: list[str]):
        """Set multiple Vorbis composers using external metaflac tool."""
        VorbisMetadataSetter.set_multiple_tags(file_path, "COMPOSER", composers)

    @staticmethod
    def set_genres(file_path: Path, genres: list[str]):
        """Set multiple Vorbis genres using external metaflac tool."""
        VorbisMetadataSetter.set_multiple_tags(file_path, "GENRE", genres)

    @staticmethod
    def set_performers(file_path: Path, performers: list[str]):
        """Set multiple Vorbis performers using external metaflac tool."""
        VorbisMetadataSetter.set_multiple_tags(file_path, "PERFORMER", performers)

    @staticmethod
    def set_multiple_comments(file_path: Path, comments: list[str]):
        """Set multiple Vorbis comments using external metaflac tool."""
        VorbisMetadataSetter.set_multiple_tags(file_path, "COMMENT", comments)

    @staticmethod
    def set_null_bytes_test_metadata(file_path: Path) -> None:
        """Set test metadata including null bytes for testing null byte handling."""
        # First remove existing ARTIST tags
        try:
            command = ["metaflac", "--remove-tag=ARTIST", str(file_path)]
            run_external_tool(command, "metaflac")
        except Exception:
            # Ignore if tags don't exist
            pass

        # Set ARTIST tags, one with null bytes
        command = ["metaflac", "--set-tag=ARTIST=Artist\x00with\x00nulls", str(file_path)]
        run_external_tool(command, "metaflac")

        command = ["metaflac", "--set-tag=ARTIST=Normal Artist", str(file_path)]
        run_external_tool(command, "metaflac")

        # Set TITLE
        command = ["metaflac", "--set-tag=TITLE=Normal Title", str(file_path)]
        run_external_tool(command, "metaflac")
