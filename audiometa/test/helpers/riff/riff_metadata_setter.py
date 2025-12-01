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
            "year": "--ICRD",
            "release_date": "--ICRD",
            "comment": "--ICMT",
            "track": "--ITRK",
            "track_number": "--ITRK",
            "bpm": "--TBPM",
            "composer": "--ICMP",
            "lyrics": "--ILYR",
            "language": "--ILNG",
            "album_artist": "--IAAR",
            "rating": "--IRTD",
            "copyright": "--ICOP",
            "isrc": "--ISRC",
        }

        # Handle list values - include first value in main command to avoid overwriting
        artist_value = None
        genre_value = None
        composer_value = None
        for key, value in metadata.items():
            if isinstance(value, list) and value:
                if key.lower() == "artist":
                    artist_value = value[0]  # Store first artist for main command
                elif key.lower() == "genre":
                    genre_value = value[0]  # Store first genre for main command
                elif key.lower() == "composer":
                    composer_value = value[0]  # Store first composer for main command

        # Handle non-list values and include list values in main command
        # Note: Rating, BPM, Language, and Composer need to be set AFTER bwfmetaedit to avoid being overwritten
        rating_value = None
        bpm_value = None
        language_value = None
        composer_single_value = None
        metadata_added = False
        for key, value in metadata.items():
            if key.lower() in key_mapping and not isinstance(value, list):
                if key.lower() == "bpm":
                    bpm_value = str(value)  # Store for later
                elif key.lower() == "rating":
                    rating_value = str(value)  # Store for later
                elif key.lower() == "language":
                    language_value = str(value)  # Store for later
                elif key.lower() == "composer":
                    composer_single_value = str(value)  # Store for later
                else:
                    cmd.extend([f"{key_mapping[key.lower()]}={value}"])
                    metadata_added = True

        # Add artist if it was provided as a list
        if artist_value is not None:
            cmd.extend([f"{key_mapping['artist']}={artist_value}"])
            metadata_added = True

        # Add genre if it was provided as a list
        if genre_value is not None:
            cmd.extend([f"{key_mapping['genre']}={genre_value}"])
            metadata_added = True

        # Run bwfmetaedit first if metadata was actually added
        if metadata_added:
            cmd.append(str(file_path))
            run_external_tool(cmd, "bwfmetaedit")

        # Set BPM, rating, and language AFTER bwfmetaedit to avoid being overwritten
        if bpm_value is not None:
            from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

            ManualRIFFMetadataCreator.create_bpm_field(file_path, bpm_value)

        if rating_value is not None:
            from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

            ManualRIFFMetadataCreator.create_rating_field(file_path, rating_value)

        if language_value is not None:
            from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

            ManualRIFFMetadataCreator.create_language_field(file_path, language_value)

        # Set composer (from list or single value) AFTER bwfmetaedit
        if composer_value is not None:
            from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

            ManualRIFFMetadataCreator.create_composer_field(file_path, composer_value)
        elif composer_single_value is not None:
            from .riff_manual_metadata_creator import ManualRIFFMetadataCreator

            ManualRIFFMetadataCreator.create_composer_field(file_path, composer_single_value)

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

    @staticmethod
    def set_bext_description(file_path: Path, description: str) -> None:
        """Set BWF bext Description field."""
        command = ["bwfmetaedit", f"--Description={description}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_bext_originator(file_path: Path, originator: str) -> None:
        """Set BWF bext Originator field."""
        command = ["bwfmetaedit", f"--Originator={originator}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_bext_originator_reference(file_path: Path, originator_reference: str) -> None:
        """Set BWF bext OriginatorReference field."""
        command = ["bwfmetaedit", f"--OriginatorReference={originator_reference}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_bext_origination_date(file_path: Path, origination_date: str) -> None:
        """Set BWF bext OriginationDate field (YYYY-MM-DD format)."""
        command = ["bwfmetaedit", f"--OriginationDate={origination_date}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_bext_origination_time(file_path: Path, origination_time: str) -> None:
        """Set BWF bext OriginationTime field (HH:MM:SS format)."""
        command = ["bwfmetaedit", f"--OriginationTime={origination_time}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_bext_time_reference(file_path: Path, time_reference: int) -> None:
        """Set BWF bext TimeReference field."""
        command = ["bwfmetaedit", f"--Timereference={time_reference}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_bext_coding_history(file_path: Path, coding_history: str) -> None:
        """Set BWF bext CodingHistory field."""
        command = ["bwfmetaedit", f"--History={coding_history}", str(file_path)]
        run_external_tool(command, "bwfmetaedit")

    @staticmethod
    def set_bext_metadata(file_path: Path, bext_metadata: dict[str, Any]) -> None:
        """Set multiple BWF bext metadata fields at once.

        Args:
            file_path: Path to WAV file
            bext_metadata: Dictionary with bext field names as keys:
                - Description: str
                - Originator: str
                - OriginatorReference: str
                - OriginationDate: str (YYYY-MM-DD format)
                - OriginationTime: str (HH:MM:SS format)
                - TimeReference: int (uint64)
                - UMID: str (hex string)
                - CodingHistory: str
                - LoudnessValue: float (LU, converted to 0.1 LU units)
                - LoudnessRange: float (LU, converted to 0.1 LU units)
                - MaxTruePeakLevel: float (dB, converted to 0.1 dB units)
                - MaxMomentaryLoudness: float (LU, converted to 0.1 LU units)
                - MaxShortTermLoudness: float (LU, converted to 0.1 LU units)
        """
        # Map bext field names to bwfmetaedit arguments
        field_mapping = {
            "Description": "--Description",
            "Originator": "--Originator",
            "OriginatorReference": "--OriginatorReference",
            "OriginationDate": "--OriginationDate",
            "OriginationTime": "--OriginationTime",
            "TimeReference": "--Timereference",
            "UMID": "--UMID",
            "CodingHistory": "--History",
            "LoudnessValue": "--LoudnessValue",
            "LoudnessRange": "--LoudnessRange",
            "MaxTruePeakLevel": "--MaxTruePeakLevel",
            "MaxMomentaryLoudness": "--MaxMomentaryLoudness",
            "MaxShortTermLoudness": "--MaxShortTermLoudness",
        }

        # Separate loudness fields from other fields
        # Loudness fields need to be set after other fields to ensure BWF v2 is created
        loudness_fields = [
            "LoudnessValue",
            "LoudnessRange",
            "MaxTruePeakLevel",
            "MaxMomentaryLoudness",
            "MaxShortTermLoudness",
        ]
        regular_fields = {}
        loudness_metadata = {}

        for field_name, value in bext_metadata.items():
            if field_name in field_mapping and value is not None:
                if field_name in loudness_fields:
                    loudness_metadata[field_name] = value
                else:
                    regular_fields[field_name] = value

        # Set regular fields first
        if regular_fields:
            cmd_regular = ["bwfmetaedit"]
            for field_name, value in regular_fields.items():
                cmd_regular.extend([f"{field_mapping[field_name]}={value}"])
            cmd_regular.append(str(file_path))
            run_external_tool(cmd_regular, "bwfmetaedit")

        # Set loudness fields in separate command (ensures BWF v2 is properly created)
        if loudness_metadata:
            cmd_loudness = ["bwfmetaedit"]
            for field_name, value in loudness_metadata.items():
                cmd_loudness.extend([f"{field_mapping[field_name]}={value}"])
            cmd_loudness.append(str(file_path))
            run_external_tool(cmd_loudness, "bwfmetaedit")
