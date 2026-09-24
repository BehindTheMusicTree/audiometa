"""Unified metadata keys for audio file metadata handling.

This module defines the standardized keys used throughout the application for representing audio metadata in a unified
format.
"""

from enum import StrEnum


class UnifiedMetadataKey(StrEnum):
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
    DISC_NUMBER = "disc_number"
    DISC_TOTAL = "disc_total"
    BPM = "bpm"
    COMPOSERS = "composer"
    PUBLISHER = "publisher"
    COPYRIGHT = "copyright"
    UNSYNCHRONIZED_LYRICS = "unsynchronized_lyrics"
    COMMENT = "comment"
    REPLAYGAIN = "replaygain"
    ARCHIVAL_LOCATION = "archival_location"
    ISRC = "isrc"
    MUSICBRAINZ_TRACKID = "musicbrainz_trackid"
    MUSICBRAINZ_ARTISTIDS = "musicbrainz_artistids"
    DESCRIPTION = "description"
    ORIGINATOR = "originator"

    def qualified_name(self) -> str:
        return f"{type(self).__name__}.{self.name}"

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
            UnifiedMetadataKey.MUSICBRAINZ_ARTISTIDS,
        }

        result = self in multi_value_fields
        if result and self.get_optional_type() != list[str]:
            msg = f"Optional type for {self} is not list"
            raise ValueError(msg)
        return result

    def get_optional_type(self) -> object:
        """Get the optional type for the metadata key.

        Returns:
            The expected type of the metadata value. This may be a concrete type (e.g. ``str``), a union
            (e.g. ``int | None``), or a generic alias (e.g. ``list[str]``) rather than always a ``type`` instance.
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
            UnifiedMetadataKey.DISC_NUMBER: int | None,
            UnifiedMetadataKey.DISC_TOTAL: int | None,
            UnifiedMetadataKey.BPM: int,
            UnifiedMetadataKey.COMPOSERS: list[str],
            UnifiedMetadataKey.PUBLISHER: str,
            UnifiedMetadataKey.COPYRIGHT: str,
            UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: str,
            UnifiedMetadataKey.COMMENT: str,
            UnifiedMetadataKey.REPLAYGAIN: str,
            UnifiedMetadataKey.ARCHIVAL_LOCATION: str,
            UnifiedMetadataKey.ISRC: str,
            UnifiedMetadataKey.MUSICBRAINZ_TRACKID: str,
            UnifiedMetadataKey.MUSICBRAINZ_ARTISTIDS: list[str],
            UnifiedMetadataKey.DESCRIPTION: str,
            UnifiedMetadataKey.ORIGINATOR: str,
        }
        result_type = app_metadata_keys_optional_types_map.get(self)
        if not result_type:
            msg = f"No optional type defined for {self}"
            raise ValueError(msg)
        return result_type
