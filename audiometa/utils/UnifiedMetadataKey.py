
from enum import Enum
from typing import Union


class UnifiedMetadataKey(str, Enum):
    TITLE = 'title'
    ARTISTS = 'artists'
    ALBUM = 'album'
    ALBUM_ARTISTS = 'album_artists'
    GENRES_NAMES = 'genres_names'
    RATING = 'rating'
    LANGUAGE = 'language'
    RELEASE_DATE = 'release_date'
    TRACK_NUMBER = 'track_number'
    BPM = 'bpm'
    COMPOSERS = 'composer'
    PUBLISHER = 'publisher'
    COPYRIGHT = 'copyright'
    UNSYNCHRONIZED_LYRICS = 'unsynchronized_lyrics'
    COMMENT = 'comment'
    REPLAYGAIN = 'replaygain'
    ARCHIVAL_LOCATION = 'archival_location'

    def can_semantically_have_multiple_values(self) -> bool:
        # Fields that can contain multiple values (lists) - only semantically meaningful ones
        multi_value_fields = {
            UnifiedMetadataKey.ARTISTS,
            UnifiedMetadataKey.ALBUM_ARTISTS,
            UnifiedMetadataKey.GENRES_NAMES,
            UnifiedMetadataKey.COMPOSERS,
        }
        
        result = self in multi_value_fields
        if result and self.get_optional_type() != list[str]:
            raise ValueError(f'Optional type for {self} is not list')
        return result

    def get_optional_type(self) -> type:
        APP_METADATA_KEYS_OPTIONAL_TYPES_MAP = {
            UnifiedMetadataKey.TITLE: str,
            UnifiedMetadataKey.ARTISTS: list[str],
            UnifiedMetadataKey.ALBUM: str,
            UnifiedMetadataKey.ALBUM_ARTISTS: list[str],
            UnifiedMetadataKey.GENRES_NAMES: list[str],
            UnifiedMetadataKey.RATING: int,
            UnifiedMetadataKey.LANGUAGE: str,
            UnifiedMetadataKey.RELEASE_DATE: str,
            UnifiedMetadataKey.TRACK_NUMBER: Union[int, str],
            UnifiedMetadataKey.BPM: int,
            UnifiedMetadataKey.COMPOSERS: list[str],
            UnifiedMetadataKey.PUBLISHER: str,
            UnifiedMetadataKey.COPYRIGHT: str,
            UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: str,
            UnifiedMetadataKey.COMMENT: str,
            UnifiedMetadataKey.REPLAYGAIN: str,
            UnifiedMetadataKey.ARCHIVAL_LOCATION: str,
        }
        type = APP_METADATA_KEYS_OPTIONAL_TYPES_MAP.get(self)
        if not type:
            raise ValueError(f'No optional type defined for {self}')
        return type
