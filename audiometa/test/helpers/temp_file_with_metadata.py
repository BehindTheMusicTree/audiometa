"""Consolidated temporary file with metadata utilities for testing.

This module provides a context manager for test files with metadata using contextlib.
"""

import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from .common import AudioFileCreator
from .id3v1 import ID3v1MetadataSetter
from .id3v2 import ID3v2MetadataSetter
from .riff import RIFFMetadataSetter
from .vorbis import VorbisMetadataSetter


@contextmanager
def temp_file_with_metadata(metadata: dict, format_type: str) -> Generator[Path, None, None]:
    """Context manager for creating temporary test files with metadata.

    This function creates a temporary audio file with the specified metadata,
    yields its path for use in tests, and automatically cleans up the file.

    Args:
        metadata: Dictionary of metadata to set on the test file
        format_type: Audio format ('mp3', 'id3v1', 'id3v2.3', 'id3v2.4', 'flac', 'wav')

    Yields:
        Path to the created test file with metadata

    Example:
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            metadata = get_unified_metadata(test_file)
    """
    target_file = _create_test_file_with_metadata(metadata, format_type)
    try:
        yield target_file
    finally:
        if target_file.exists():
            target_file.unlink()


def _create_test_file_with_metadata(metadata: dict, format_type: str) -> Path:
    """Create a test file with specific metadata values.

    This function uses external tools to set specific metadata values
    without using the app's update functions, improving test isolation.

    Args:
        metadata: Dictionary of metadata to set
        format_type: Audio format ('mp3', 'id3v1', 'flac', 'wav')

    Returns:
        Path to the created file with metadata
    """
    # Create temporary file with correct extension
    # For id3v1, id3v2.3, id3v2.4, use .mp3 extension since they're still MP3 files
    actual_extension = "mp3" if format_type.lower() in ["id3v1", "id3v2.3", "id3v2.4"] else format_type.lower()
    with tempfile.NamedTemporaryFile(suffix=f".{actual_extension}", delete=False) as tmp_file:
        target_file = Path(tmp_file.name)

    assets_dir = Path(__file__).parent.parent.parent / "test" / "assets"
    AudioFileCreator.create_minimal_audio_file(target_file, format_type, assets_dir)

    if format_type.lower() == "mp3":
        ID3v2MetadataSetter.set_metadata(target_file, metadata)
    elif format_type.lower() == "id3v1":
        ID3v1MetadataSetter.set_metadata(target_file, metadata)
    elif format_type.lower() in ["id3v2.3", "id3v2.4"]:
        # Use version-specific ID3v2 metadata setting
        version = format_type.lower().replace("id3v2.", "2.")
        ID3v2MetadataSetter.set_metadata(target_file, metadata, version)
    elif format_type.lower() == "flac":
        VorbisMetadataSetter.set_metadata(target_file, metadata)
    elif format_type.lower() == "wav":
        RIFFMetadataSetter.set_metadata(target_file, metadata)
    else:
        msg = f"Unsupported format type: {format_type}"
        raise ValueError(msg)

    return target_file
