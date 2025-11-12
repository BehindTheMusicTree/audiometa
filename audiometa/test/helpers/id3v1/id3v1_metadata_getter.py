"""ID3v1 metadata inspection utilities for testing audio file metadata."""

from pathlib import Path
from typing import Any


class ID3v1MetadataGetter:
    """Utilities for inspecting ID3v1 metadata in audio files."""

    @staticmethod
    def get_raw_metadata(file_path: Path) -> dict[str, Any]:
        """Return the raw metadata for a specific ID3v1 field."""
        with file_path.open("rb") as f:
            f.seek(-128, 2)  # Seek to last 128 bytes (ID3v1 tag location)
            data = f.read(128)

        # Check for ID3v1 tag header
        if not data.startswith(b"TAG"):
            return {}

        # Determine if it's ID3v1.1 (has track number)
        is_id3v1_1 = data[125] != 0

        # Parse fields based on ID3v1 specification
        field_info = {
            "title": (3, 33, 30),  # bytes 3-32, 30 chars max
            "artist": (33, 63, 30),  # bytes 33-62, 30 chars max
            "album": (63, 93, 30),  # bytes 63-92, 30 chars max
            "year": (93, 97, 4),  # bytes 93-96, 4 chars max
            "genre": (127, 128, 1),  # byte 127
        }

        if is_id3v1_1:
            field_info["comment"] = (97, 125, 28)  # bytes 97-124, 28 chars max (ID3v1.1)
            field_info["track"] = (125, 126, 1)  # byte 125 (ID3v1.1)
        else:
            field_info["comment"] = (97, 127, 30)  # bytes 97-126, 30 chars max (ID3v1)

        metadata: dict[str, str | int | None] = {}
        for field, (start, end, _max_chars) in field_info.items():
            raw_bytes = data[start:end]
            if field in ["title", "artist", "album", "year", "comment"]:
                metadata[field] = raw_bytes.decode("latin-1").rstrip("\x00")
            elif field == "track":
                metadata[field] = raw_bytes[0] if raw_bytes and raw_bytes[0] != 0 else None
            elif field == "genre":
                metadata[field] = raw_bytes[0] if raw_bytes else 0

        # Handle ID3v1 track number stored in comment field (non-standard but common)
        if "track" not in metadata or metadata["track"] is None:
            comment = metadata.get("comment", "")
            if isinstance(comment, str) and len(comment) == 30 and comment[-1] != "\x00":
                metadata["track"] = ord(comment[-1])
                metadata["comment"] = comment[:-1].rstrip("\x00")

        return metadata

    @staticmethod
    def get_title(file_path):
        metadata = ID3v1MetadataGetter.get_raw_metadata(file_path)
        return metadata.get("title", "")
