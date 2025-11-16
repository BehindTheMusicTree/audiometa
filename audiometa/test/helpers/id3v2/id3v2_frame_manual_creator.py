#!/usr/bin/env python3
"""Manual implementation to create multiple separate ID3v2 frames for testing.

This bypasses standard tools and libraries that automatically consolidate frames, allowing creation of test files with
truly separate TPE1, TPE2, TCON etc. frames.
"""

import struct
import subprocess
import tempfile
from pathlib import Path

from audiometa.utils.tool_path_resolver import get_tool_path


class ManualID3v2FrameCreator:
    """Creates ID3v2 tags with multiple separate frames by manual binary construction."""

    @staticmethod
    def create_multiple_tpe1_frames(file_path: Path, artists: list[str], version: str = "2.4") -> None:
        if version not in ["2.3", "2.4"]:
            msg = "Version must be '2.3' or '2.4'"
            raise ValueError(msg)
        frames = []
        for artist in artists:
            frame_data = ManualID3v2FrameCreator._create_text_frame("TPE1", artist, version)
            frames.append(frame_data)

        ManualID3v2FrameCreator._write_id3v2_tag(file_path, frames, version)

    @staticmethod
    def create_multiple_tpe2_frames(file_path: Path, album_artists: list[str], version: str = "2.4") -> None:
        if version not in ["2.3", "2.4"]:
            msg = "Version must be '2.3' or '2.4'"
            raise ValueError(msg)
        frames = []
        for album_artist in album_artists:
            frame_data = ManualID3v2FrameCreator._create_text_frame("TPE2", album_artist, version)
            frames.append(frame_data)

        ManualID3v2FrameCreator._write_id3v2_tag(file_path, frames, version)

    @staticmethod
    def create_multiple_tcon_frames(file_path: Path, genres: list[str], version: str = "2.4") -> None:
        if version not in ["2.3", "2.4"]:
            msg = "Version must be '2.3' or '2.4'"
            raise ValueError(msg)
        frames = []
        for genre in genres:
            frame_data = ManualID3v2FrameCreator._create_text_frame("TCON", genre, version)
            frames.append(frame_data)

        ManualID3v2FrameCreator._write_id3v2_tag(file_path, frames, version)

    @staticmethod
    def create_multiple_tcom_frames(file_path: Path, composers: list[str], version: str = "2.4") -> None:
        if version not in ["2.3", "2.4"]:
            msg = "Version must be '2.3' or '2.4'"
            raise ValueError(msg)
        frames = []
        for composer in composers:
            frame_data = ManualID3v2FrameCreator._create_text_frame("TCOM", composer, version)
            frames.append(frame_data)

        ManualID3v2FrameCreator._write_id3v2_tag(file_path, frames, version)

    @staticmethod
    def create_mixed_multiple_frames(
        file_path: Path, artists: list[str], genres: list[str], version: str = "2.4"
    ) -> None:
        if version not in ["2.3", "2.4"]:
            msg = "Version must be '2.3' or '2.4'"
            raise ValueError(msg)
        frames = []

        # Add multiple TPE1 frames
        for artist in artists:
            frame_data = ManualID3v2FrameCreator._create_text_frame("TPE1", artist, version)
            frames.append(frame_data)

        # Add multiple TCON frames
        for genre in genres:
            frame_data = ManualID3v2FrameCreator._create_text_frame("TCON", genre, version)
            frames.append(frame_data)

        ManualID3v2FrameCreator._write_id3v2_tag(file_path, frames, version)

    @staticmethod
    def _create_text_frame(frame_id: str, text: str, version: str, encoding: int | None = None) -> bytes:
        """Create a single ID3v2 text frame with the given ID and text."""
        # Choose encoding based on version or provided encoding
        if encoding is not None:
            enc = encoding
        elif version == "2.3":
            # ID3v2.3: Use ISO-8859-1
            enc = 0
        else:  # ID3v2.4
            # ID3v2.4: Use UTF-8
            enc = 3

        # Determine null terminator based on encoding
        null_terminator = b"\x00\x00" if enc in (1, 2) else b"\x00"

        # Encode text
        if enc == 0:  # ISO-8859-1
            text_bytes = text.encode("latin1", errors="ignore")
        elif enc == 1:  # UTF-16 with BOM
            text_bytes = text.encode("utf-16")
        elif enc == 2:  # UTF-16BE without BOM
            text_bytes = text.encode("utf-16be")
        elif enc == 3:  # UTF-8
            text_bytes = text.encode("utf-8")
        else:
            text_bytes = text.encode("latin1", errors="ignore")

        # Frame data: encoding byte + text + null terminator
        frame_data = struct.pack("B", enc) + text_bytes + null_terminator

        # Frame header: ID (4 bytes) + size (4 bytes) + flags (2 bytes)
        frame_id_bytes = frame_id.encode("ascii")
        frame_size = len(frame_data)
        frame_flags = 0x0000  # No flags

        if version == "2.3":
            frame_header = (
                frame_id_bytes
                + struct.pack(">I", frame_size)  # Big-endian 32-bit size
                + struct.pack(">H", frame_flags)  # Big-endian 16-bit flags
            )
        else:  # ID3v2.4
            frame_header = (
                frame_id_bytes
                + ManualID3v2FrameCreator._synchsafe_int(frame_size)  # Synchsafe size
                + struct.pack(">H", frame_flags)  # Big-endian 16-bit flags
            )

        return frame_header + frame_data

    @staticmethod
    def _synchsafe_int(value: int) -> bytes:
        """Convert integer to ID3v2 synchsafe integer (7 bits per byte)."""
        # Split into 7-bit chunks, most significant first
        result: list[int] = []
        for _i in range(4):
            result.insert(0, value & 0x7F)
            value >>= 7
        return struct.pack("4B", *result)

    @staticmethod
    def _write_id3v2_tag(file_path: Path, frames: list[bytes], version: str) -> None:
        """Write ID3v2 tag with the given frames to the file."""
        # Calculate total size of all frames
        frames_data = b"".join(frames)
        tag_size = len(frames_data)

        # Create header based on version
        if version == "2.3":
            # ID3v2.3 header: "ID3" + version + flags + size (regular integer)
            header = (
                b"ID3"  # ID3 identifier
                + struct.pack("BB", 3, 0)  # Version 2.3.0
                + struct.pack("B", 0)  # Flags (no unsynchronisation, etc.)
                + struct.pack(">I", tag_size)  # Size as regular 32-bit integer
            )
        else:  # ID3v2.4
            # ID3v2.4 header: "ID3" + version + flags + size (synchsafe integer)
            header = (
                b"ID3"  # ID3 identifier
                + struct.pack("BB", 4, 0)  # Version 2.4.0
                + struct.pack("B", 0)  # Flags (no unsynchronisation, etc.)
                + ManualID3v2FrameCreator._synchsafe_int(tag_size)  # Size as synchsafe integer
            )

        # Read existing file content (audio data)
        with file_path.open("rb") as f:
            original_data = f.read()

        # Remove any existing ID3v2 tag
        audio_data = original_data
        if original_data.startswith(b"ID3") and len(original_data) >= 10:
            # Skip existing ID3v2 tag
            # Extract version and size from existing tag
            existing_version = original_data[3]
            size_bytes = original_data[6:10]

            if existing_version == 4:
                # ID3v2.4 uses synchsafe integers
                existing_tag_size = 0
                for byte in size_bytes:
                    existing_tag_size = (existing_tag_size << 7) | (byte & 0x7F)
            else:
                # ID3v2.3 and earlier use regular integers
                existing_tag_size = struct.unpack(">I", size_bytes)[0]

            # Audio data starts after header (10 bytes) + tag size
            audio_data = original_data[10 + existing_tag_size :]

        # Write new file with our custom ID3v2 tag
        with file_path.open("wb") as f:
            f.write(header)
            f.write(frames_data)
            f.write(audio_data)


def manual_multiple_frames_test():
    """Test the manual frame creation for both ID3v2.3 and ID3v2.4."""

    def run_test_for_version(version: str):
        """Test a specific ID3v2 version."""

        # Create a temporary MP3 file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Create minimal MP3 file
            subprocess.run(
                ["ffmpeg", "-f", "lavfi", "-i", "anullsrc=duration=1", "-acodec", "mp3", "-y", str(tmp_path)],
                check=True,
                capture_output=True,
            )

            # Test 1: Multiple TPE1 frames
            artists = ["Artist One", "Artist Two", "Artist Three"]
            ManualID3v2FrameCreator.create_multiple_tpe1_frames(tmp_path, artists, version)

            # Check result with mid3v2
            result = subprocess.run(
                [get_tool_path("mid3v2"), "-l", str(tmp_path)], capture_output=True, text=True, check=False
            )

            # Count TPE1 occurrences
            tpe1_count = result.stdout.count("TPE1=")

            if tpe1_count > 1:
                pass
            else:
                pass

            # Test 2: Multiple TCON frames
            genres = ["Rock", "Pop", "Alternative"]
            ManualID3v2FrameCreator.create_multiple_tcon_frames(tmp_path, genres, version)

            result = subprocess.run(
                [get_tool_path("mid3v2"), "-l", str(tmp_path)], capture_output=True, text=True, check=False
            )

            tcon_count = result.stdout.count("TCON=")

            # Test 3: Mixed multiple frames
            ManualID3v2FrameCreator.create_mixed_multiple_frames(
                tmp_path, artists=["Artist A", "Artist B"], genres=["Genre X", "Genre Y"], version=version
            )

            result = subprocess.run(
                [get_tool_path("mid3v2"), "-l", str(tmp_path)], capture_output=True, text=True, check=False
            )

            # Check version in the file and verify multiple frames exist in binary
            result = subprocess.run(
                [get_tool_path("mid3v2"), "-l", str(tmp_path)], capture_output=True, text=True, check=False
            )
            if result.stdout:
                # Verify multiple frames exist by checking raw binary
                with Path(tmp_path).open("rb") as f:
                    data = f.read(1000)  # Read first 1KB to check for multiple frame IDs
                    tpe1_count = data.count(b"TPE1")
                    tcon_count = data.count(b"TCON")

                    if tpe1_count > 1 or tcon_count > 1:
                        pass
                    else:
                        pass

        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    # Test both versions
    run_test_for_version("2.3")
    run_test_for_version("2.4")


def create_test_file_with_version(
    output_path: Path, version: str = "2.4", artists: list[str] | None = None, genres: list[str] | None = None
) -> None:
    """Create a test MP3 file with multiple frames in the specified ID3v2 version."""
    if artists is None:
        artists = ["Artist One", "Artist Two", "Artist Three"]
    if genres is None:
        genres = ["Rock", "Pop", "Alternative"]

    # Create minimal MP3 file
    subprocess.run(
        ["ffmpeg", "-f", "lavfi", "-i", "anullsrc=duration=1", "-acodec", "mp3", "-y", str(output_path)],
        check=True,
        capture_output=True,
    )

    # Add multiple frames
    ManualID3v2FrameCreator.create_mixed_multiple_frames(output_path, artists, genres, version)


if __name__ == "__main__":
    manual_multiple_frames_test()
