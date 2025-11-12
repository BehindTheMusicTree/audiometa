"""Tag type constants for audio metadata handling.

This module defines the supported metadata formats and their file extension priorities for reading and writing audio
metadata across different file types.
"""

from enum import Enum


class MetadataFormat(str, Enum):
    """Enumeration of supported audio metadata formats."""

    ID3V2 = "id3v2"
    ID3V1 = "id3v1"
    VORBIS = "vorbis"
    RIFF = "riff"

    @classmethod
    def get_priorities(cls) -> dict[str, list["MetadataFormat"]]:
        """Get tag format priorities for different file formats.

        First tag format in each list has highest priority.

        Returns:
            dictionary mapping file extensions to ordered list of tag types
        """
        return {
            ".flac": [cls.VORBIS, cls.ID3V2, cls.ID3V1],
            ".mp3": [cls.ID3V2, cls.ID3V1],
            ".wav": [cls.RIFF, cls.ID3V2, cls.ID3V1],
        }
