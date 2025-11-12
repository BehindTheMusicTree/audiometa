"""ID3v1 raw metadata handling."""

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mutagen._file import FileType

from ._constants import (
    ID3V1_MIN_COMMENT_LENGTH_FOR_TRACK_NUMBER,
    ID3V1_TAG_SIZE,
    ID3V1_TRACK_NUMBER_POSITION,
    ID3V1_TRACK_NUMBER_VALUE_POSITION,
)
from .id3v1_raw_metadata_key import Id3v1RawMetadataKey


class Id3v1RawMetadata(FileType):
    """A custom file-like object for ID3v1 tags, providing a consistent interface similar to mutagen.

    This class encapsulates the ID3v1 128-byte structure and provides a clean interface for accessing and modifying tag
    data. It supports both reading and writing using direct file manipulation.
    """

    @dataclass
    class Id3v1Tag:
        title: str = ""
        artists_names_str: str = ""
        album_name: str = ""
        year: str = ""
        comment: str = ""
        track_number: int | None = None
        genre_code: int = 255  # 255 is undefined genre

    def __init__(self, fileobj: Any):
        self.fileobj = fileobj
        object.__setattr__(self, "tags", None)
        self._load_tags()

    def _load_tags(self) -> None:
        # Handle both file objects and file paths
        if isinstance(self.fileobj, str | Path):
            with Path(self.fileobj).open("rb") as f:
                f.seek(-ID3V1_TAG_SIZE, 2)  # Seek from end
                data = f.read(ID3V1_TAG_SIZE)
        else:
            self.fileobj.seek(-ID3V1_TAG_SIZE, 2)  # Seek from end
            data = self.fileobj.read(ID3V1_TAG_SIZE)

        if not data.startswith(b"TAG"):
            self.tags = None
            return

        # Parse the fixed structure into our tag object
        tag = self.Id3v1Tag(
            title=data[3:33].strip(b"\0").decode("latin1", "replace"),
            artists_names_str=data[33:63].strip(b"\0").decode("latin1", "replace"),
            album_name=data[63:93].strip(b"\0").decode("latin1", "replace"),
            year=data[93:97].strip(b"\0").decode("latin1", "replace"),
            genre_code=struct.unpack("B", data[127:128])[0],
        )

        # Handle ID3v1.1 track number in comment field
        try:
            comment = data[97:127]

            # Check for ID3v1.1 track number format (bytes 125-126)
            if (
                len(comment) >= ID3V1_MIN_COMMENT_LENGTH_FOR_TRACK_NUMBER
                and comment[ID3V1_TRACK_NUMBER_POSITION] == 0
                and comment[ID3V1_TRACK_NUMBER_VALUE_POSITION] != 0
            ):
                # ID3v1.1 format: track number in last two bytes
                tag.track_number = comment[ID3V1_TRACK_NUMBER_VALUE_POSITION]
                tag.comment = comment[:ID3V1_TRACK_NUMBER_POSITION].strip(b"\0").decode("latin1", "replace")
            else:
                # Regular ID3v1 format: no track number
                tag.track_number = None
                tag.comment = comment.strip(b"\0").decode("latin1", "replace")
        except Exception:
            pass

        # Convert to dictionary format similar to other metadata formats
        tags_dict: dict[Id3v1RawMetadataKey, list[str]] = {}
        if tag.title:
            tags_dict[Id3v1RawMetadataKey.TITLE] = [tag.title]
        if tag.artists_names_str:
            tags_dict[Id3v1RawMetadataKey.ARTISTS_NAMES_STR] = [tag.artists_names_str]
        if tag.album_name:
            tags_dict[Id3v1RawMetadataKey.ALBUM] = [tag.album_name]
        if tag.year:
            tags_dict[Id3v1RawMetadataKey.YEAR] = [tag.year]
        if tag.genre_code is not None:
            tags_dict[Id3v1RawMetadataKey.GENRE_CODE_OR_NAME] = [str(tag.genre_code)]
        if tag.track_number and tag.track_number != 0:
            tags_dict[Id3v1RawMetadataKey.TRACK_NUMBER] = [str(tag.track_number)]
        if tag.comment:
            tags_dict[Id3v1RawMetadataKey.COMMENT] = [tag.comment]
        object.__setattr__(self, "tags", tags_dict)

    def save(self) -> None:
        """Save ID3v1 metadata to file using direct file manipulation."""
        if not self.tags:
            return

        # Read the entire file
        if isinstance(self.fileobj, str | Path):  # type: ignore[unreachable]
            # File path
            with Path(self.fileobj).open("rb") as f:
                file_data = bytearray(f.read())
        else:
            # File object - use the same pattern as _load_tags
            self.fileobj.seek(0)
            file_data = bytearray(self.fileobj.read())

        # Create ID3v1 tag data
        tag_data = self._create_id3v1_tag_data()

        # Remove existing ID3v1 tag if present
        self._remove_existing_id3v1_tag(file_data)

        # Append new ID3v1 tag
        file_data.extend(tag_data)

        # Write back to file
        if isinstance(self.fileobj, str | Path):
            # File path
            with Path(self.fileobj).open("wb") as f:
                f.write(file_data)
        else:
            # File object
            self.fileobj.seek(0)
            self.fileobj.write(file_data)
            self.fileobj.truncate()

    def _create_id3v1_tag_data(self) -> bytes:
        """Create 128-byte ID3v1 tag data from current tags."""
        from typing import cast as type_cast

        tags: dict[Id3v1RawMetadataKey, list[str]] = type_cast(dict[Id3v1RawMetadataKey, list[str]], self.tags)
        if not tags:
            msg = "Tags must be loaded before creating tag data"
            raise ValueError(msg)
        # Initialize with null bytes
        tag_data = bytearray(ID3V1_TAG_SIZE)

        # TAG identifier (bytes 0-2)
        tag_data[0:3] = b"TAG"

        # Title (bytes 3-32, 30 chars max)
        title = tags.get(Id3v1RawMetadataKey.TITLE, [""])[0]
        title_bytes = self._truncate_string(title, 30).encode("latin-1", errors="ignore")
        tag_data[3 : 3 + len(title_bytes)] = title_bytes

        # Artist (bytes 33-62, 30 chars max)
        artist = tags.get(Id3v1RawMetadataKey.ARTISTS_NAMES_STR, [""])[0]
        artist_bytes = self._truncate_string(artist, 30).encode("latin-1", errors="ignore")
        tag_data[33 : 33 + len(artist_bytes)] = artist_bytes

        # Album (bytes 63-92, 30 chars max)
        album = tags.get(Id3v1RawMetadataKey.ALBUM, [""])[0]
        album_bytes = self._truncate_string(album, 30).encode("latin-1", errors="ignore")
        tag_data[63 : 63 + len(album_bytes)] = album_bytes

        # Year (bytes 93-96, 4 chars max)
        year = tags.get(Id3v1RawMetadataKey.YEAR, [""])[0]
        year_bytes = self._truncate_string(year, 4).encode("latin-1", errors="ignore")
        tag_data[93 : 93 + len(year_bytes)] = year_bytes

        # Comment and track number (bytes 97-126, 28 chars for comment + 2 for track)
        comment = tags.get(Id3v1RawMetadataKey.COMMENT, [""])[0]
        comment_bytes = self._truncate_string(comment, 28).encode("latin-1", errors="ignore")
        tag_data[97 : 97 + len(comment_bytes)] = comment_bytes

        # Track number (bytes 125-126 for ID3v1.1)
        track_number = tags.get(Id3v1RawMetadataKey.TRACK_NUMBER, ["0"])[0]
        if track_number and track_number != "0":
            track_num = max(0, min(255, int(track_number)))
            if track_num > 0:
                tag_data[125] = 0  # Null byte to indicate track number presence
                tag_data[126] = track_num

        # Genre (byte 127)
        genre_code = tags.get(Id3v1RawMetadataKey.GENRE_CODE_OR_NAME, ["255"])[0]
        try:
            tag_data[127] = int(genre_code)
        except ValueError:
            tag_data[127] = 255  # Unknown genre

        return bytes(tag_data)

    def _remove_existing_id3v1_tag(self, file_data: bytearray) -> bool:
        """Remove existing ID3v1 tag from file data if present.

        Returns:
            bool: True if a tag was removed, False otherwise
        """
        if len(file_data) >= ID3V1_TAG_SIZE:
            # Check if last 128 bytes contain ID3v1 tag
            last_128 = file_data[-ID3V1_TAG_SIZE:]
            if last_128[:3] == b"TAG":
                # Remove the last 128 bytes
                del file_data[-ID3V1_TAG_SIZE:]
                return True
        return False

    def _truncate_string(self, text: str, max_length: int) -> str:
        """Truncate string to maximum length, handling encoding properly."""
        if len(text) <= max_length:
            return text
        return text[:max_length]

    @property
    def mime(self) -> list[str]:
        """Return a list of MIME types this file type could be."""
        return ["audio/mpeg"]  # ID3v1 is typically used with MP3 files

    def add_tags(self) -> None:
        """Add a new ID3v1 tag to the file."""
        if self.tags is None:
            object.__setattr__(self, "tags", {})

    def delete(self, filename: str) -> None:
        """Remove tags from a file."""
        try:
            # Read the entire file
            with Path(filename).open("rb") as f:
                file_data = bytearray(f.read())

            # Remove existing ID3v1 tag if present
            if self._remove_existing_id3v1_tag(file_data):
                # Write back to file
                with Path(filename).open("wb") as f:
                    f.write(file_data)
        except Exception:
            pass  # Ignore errors during deletion

    @staticmethod
    def score(_filename: str, _fileobj: Any, _header: Any) -> int:
        """Return a score indicating how likely this class can handle the file."""
        return 0  # We don't want this to be auto-detected by mutagen
