"""Unified metadata keys for audio file metadata handling.

This module defines the standardized keys used throughout the application for representing audio metadata in a unified
format.
"""

from enum import Enum
from typing import cast


class UnifiedMetadataKey(str, Enum):
    """Enumeration of unified metadata keys used for audio file metadata."""

    TITLE = "title"
    ARTISTS = "artists"
    ALBUM = "album"
    ALBUM_ARTISTS = "album_artists"
    GENRES_NAMES = "genres_names"
    RATING = "rating"
    LANGUAGE = "language"
    RELEASE_DATE = "release_date"
    TRACK_NUMBER = "track_number"
    BPM = "bpm"
    COMPOSERS = "composer"
    PUBLISHER = "publisher"
    COPYRIGHT = "copyright"
    UNSYNCHRONIZED_LYRICS = "unsynchronized_lyrics"
    COMMENT = "comment"
    REPLAYGAIN = "replaygain"
    ARCHIVAL_LOCATION = "archival_location"

    def can_semantically_have_multiple_values(self) -> bool:
        """Check if the metadata key can semantically have multiple values.

        Returns:
            True if the key can have multiple values, False otherwise.
        """
        # Fields that can contain multiple values (lists) - only semantically meaningful ones
        multi_value_fields = {
            UnifiedMetadataKey.ARTISTS,
            UnifiedMetadataKey.ALBUM_ARTISTS,
            UnifiedMetadataKey.GENRES_NAMES,
            UnifiedMetadataKey.COMPOSERS,
        }

        result = self in multi_value_fields
        if result and self.get_optional_type() != list[str]:
            msg = f"Optional type for {self} is not list"
            raise ValueError(msg)
        return result

    def get_optional_type(self) -> type[int | float | str | list[str]]:
        """Get the optional type for the metadata key.

        Returns:
            The type of the metadata value.
        """
        app_metadata_keys_optional_types_map: dict[UnifiedMetadataKey, object] = {
            UnifiedMetadataKey.TITLE: str,
            UnifiedMetadataKey.ARTISTS: list[str],
            UnifiedMetadataKey.ALBUM: str,
            UnifiedMetadataKey.ALBUM_ARTISTS: list[str],
            UnifiedMetadataKey.GENRES_NAMES: list[str],
            UnifiedMetadataKey.RATING: int | float,
            UnifiedMetadataKey.LANGUAGE: str,
            UnifiedMetadataKey.RELEASE_DATE: str,
            UnifiedMetadataKey.TRACK_NUMBER: str,  # Can be int or str
            UnifiedMetadataKey.BPM: int,
            UnifiedMetadataKey.COMPOSERS: list[str],
            UnifiedMetadataKey.PUBLISHER: str,
            UnifiedMetadataKey.COPYRIGHT: str,
            UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: str,
            UnifiedMetadataKey.COMMENT: str,
            UnifiedMetadataKey.REPLAYGAIN: str,
            UnifiedMetadataKey.ARCHIVAL_LOCATION: str,
        }
        result_type = app_metadata_keys_optional_types_map.get(self)
        if not result_type:
            msg = f"No optional type defined for {self}"
            raise ValueError(msg)
        return cast(type[int | float | str | list[str]], result_type)
