#!/usr/bin/env python3
"""Manual implementation to create multiple separate RIFF metadata fields for testing.

This bypasses standard tools and libraries that typically overwrite fields with the same FourCC, allowing creation of
test files with truly separate IART, IGNR, etc. fields within the same INFO chunk.
"""

import struct
from pathlib import Path


class ManualRIFFMetadataCreator:
    """Creates RIFF INFO chunks with multiple separate fields by manual binary construction."""

    @staticmethod
    def create_multiple_title_fields(file_path: Path, titles: list[str]) -> None:
        """Create multiple separate INAM fields in the RIFF INFO chunk."""
        fields = []
        for title in titles:
            field_data = ManualRIFFMetadataCreator._create_info_field("INAM", title)
            fields.append(field_data)

        ManualRIFFMetadataCreator._write_riff_info_chunk(file_path, fields)

    @staticmethod
    def create_multiple_artist_fields(file_path: Path, artists: list[str]) -> None:
        """Create multiple separate IART fields in the RIFF INFO chunk."""
        fields = []
        for artist in artists:
            field_data = ManualRIFFMetadataCreator._create_info_field("IART", artist)
            fields.append(field_data)

        ManualRIFFMetadataCreator._write_riff_info_chunk(file_path, fields)

    @staticmethod
    def create_multiple_genre_fields(file_path: Path, genres: list[str]) -> None:
        """Create multiple separate IGNR fields in the RIFF INFO chunk."""
        fields = []
        for genre in genres:
            field_data = ManualRIFFMetadataCreator._create_info_field("IGNR", genre)
            fields.append(field_data)

        ManualRIFFMetadataCreator._write_riff_info_chunk(file_path, fields)

    @staticmethod
    def create_multiple_composer_fields(file_path: Path, composers: list[str]) -> None:
        """Create multiple separate ICMP fields in the RIFF INFO chunk."""
        fields = []
        for composer in composers:
            field_data = ManualRIFFMetadataCreator._create_info_field("ICMP", composer)
            fields.append(field_data)

        ManualRIFFMetadataCreator._write_riff_info_chunk(file_path, fields)

    @staticmethod
    def create_multiple_album_artist_fields(file_path: Path, album_artists: list[str]) -> None:
        """Create multiple separate IAAR fields in the RIFF INFO chunk."""
        fields = []
        for album_artist in album_artists:
            field_data = ManualRIFFMetadataCreator._create_info_field("IAAR", album_artist)
            fields.append(field_data)

        ManualRIFFMetadataCreator._write_riff_info_chunk(file_path, fields)

    @staticmethod
    def create_multiple_comment_fields(file_path: Path, comments: list[str]) -> None:
        """Create multiple separate ICMT fields in the RIFF INFO chunk."""
        fields = []
        for comment in comments:
            field_data = ManualRIFFMetadataCreator._create_info_field("ICMT", comment)
            fields.append(field_data)

        ManualRIFFMetadataCreator._write_riff_info_chunk(file_path, fields)

    @staticmethod
    def create_mixed_multiple_fields(file_path: Path, artists: list[str], genres: list[str]) -> None:
        """Create multiple fields of different types in the RIFF INFO chunk."""
        fields = []

        # Add multiple IART fields
        for artist in artists:
            field_data = ManualRIFFMetadataCreator._create_info_field("IART", artist)
            fields.append(field_data)

        # Add multiple IGNR fields
        for genre in genres:
            field_data = ManualRIFFMetadataCreator._create_info_field("IGNR", genre)
            fields.append(field_data)

        ManualRIFFMetadataCreator._write_riff_info_chunk(file_path, fields)

    @staticmethod
    def create_bpm_field(file_path: Path, bpm: str) -> None:
        """Create IBPM field in the RIFF INFO chunk."""
        field_data = ManualRIFFMetadataCreator._create_info_field("IBPM", bpm)
        ManualRIFFMetadataCreator._write_riff_info_chunk(file_path, [field_data])

    @staticmethod
    def create_lyrics_field(file_path: Path, lyrics: str) -> None:
        """Create ILYR field in the RIFF INFO chunk."""
        field_data = ManualRIFFMetadataCreator._create_info_field("ILYR", lyrics)
        ManualRIFFMetadataCreator._write_riff_info_chunk(file_path, [field_data])

    @staticmethod
    def _create_info_field(field_id: str, text: str) -> bytes:
        """Create a single RIFF INFO field with the given FourCC and text."""
        # Encode text as UTF-8 with null terminator
        text_bytes = text.encode("utf-8") + b"\x00"

        # Ensure proper word alignment (pad to even length)
        if len(text_bytes) % 2:
            text_bytes += b"\x00"

        # RIFF field structure: FourCC (4 bytes) + size (4 bytes) + data
        field_id_bytes = field_id.encode("ascii")
        field_size = len(text_bytes)

        field_header = field_id_bytes + struct.pack("<I", field_size)  # Little-endian 32-bit size

        return field_header + text_bytes

    @staticmethod
    def _write_riff_info_chunk(file_path: Path, fields: list[bytes]) -> None:
        """Write RIFF INFO chunk with the given fields to the file."""
        # Read existing file content
        with file_path.open("rb") as f:
            original_data = f.read()

        # Skip any ID3v2 tags that might be present at the start
        audio_data = ManualRIFFMetadataCreator._skip_id3v2_tags(original_data)

        # Validate RIFF/WAVE header
        if len(audio_data) < 12 or audio_data[:4] != b"RIFF" or audio_data[8:12] != b"WAVE":
            msg = "Invalid WAV file format"
            raise ValueError(msg)

        # Find existing INFO chunk and remove it
        audio_data_without_info = ManualRIFFMetadataCreator._remove_existing_info_chunk(audio_data)

        # Calculate total size of all fields
        fields_data = b"".join(fields)

        # Create new INFO chunk
        # LIST chunk structure: 'LIST' + size + type + data
        info_chunk_data = b"INFO" + fields_data
        info_chunk_size = len(info_chunk_data)

        new_info_chunk = (
            b"LIST"  # LIST chunk identifier
            + struct.pack("<I", info_chunk_size)  # Chunk size (little-endian)
            + info_chunk_data  # INFO type + field data
        )

        # Insert new INFO chunk after RIFF header (after first 12 bytes)
        new_file_data = (
            audio_data_without_info[:12]  # RIFF header
            + new_info_chunk  # New INFO chunk
            + audio_data_without_info[12:]  # Rest of audio data
        )

        # Update RIFF file size (total file size - 8 bytes for RIFF header)
        total_size = len(new_file_data) - 8
        new_file_data = (
            new_file_data[:4]  # 'RIFF'
            + struct.pack("<I", total_size)  # Updated size
            + new_file_data[8:]  # Rest of data
        )

        # Write new file
        with file_path.open("wb") as f:
            f.write(new_file_data)

    @staticmethod
    def _skip_id3v2_tags(data: bytes) -> bytes:
        """Skip ID3v2 tags if present at the start of the file."""
        if data.startswith(b"ID3"):
            if len(data) < 10:
                return data

            # Get size from synchsafe integer (7 bits per byte)
            size_bytes = data[6:10]
            size = (
                ((size_bytes[0] & 0x7F) << 21)
                | ((size_bytes[1] & 0x7F) << 14)
                | ((size_bytes[2] & 0x7F) << 7)
                | (size_bytes[3] & 0x7F)
            )

            # Skip the header (10 bytes) plus the size of the tag
            return data[10 + size :]
        return data

    @staticmethod
    def _remove_existing_info_chunk(data: bytes) -> bytes:
        """Remove existing INFO chunk from RIFF data if present."""
        if len(data) < 12:
            return data

        result = bytearray(data[:12])  # Keep RIFF header
        pos = 12  # Start after RIFF header

        while pos < len(data) - 8:
            chunk_id = data[pos : pos + 4]
            chunk_size = struct.unpack("<I", data[pos + 4 : pos + 8])[0]

            # Skip INFO chunk, keep others
            if chunk_id == b"LIST" and pos + 12 <= len(data) and data[pos + 8 : pos + 12] == b"INFO":
                # Skip this INFO chunk entirely
                pos += 8 + ((chunk_size + 1) & ~1)  # Move to next chunk with alignment
            else:
                # Keep this chunk
                chunk_end = pos + 8 + ((chunk_size + 1) & ~1)  # Include padding for alignment
                result.extend(data[pos:chunk_end])
                pos = chunk_end

        return bytes(result)
