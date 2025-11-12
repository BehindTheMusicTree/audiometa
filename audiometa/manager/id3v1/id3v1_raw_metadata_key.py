from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

from ...utils.types import RawMetadataKey


class Id3v1RawMetadataKey(RawMetadataKey):
    TITLE = UnifiedMetadataKey.TITLE
    ARTISTS_NAMES_STR = UnifiedMetadataKey.ARTISTS
    ALBUM = UnifiedMetadataKey.ALBUM
    GENRE_CODE_OR_NAME = "GENRE_CODE_OR_NAME"
    YEAR = "YEAR"
    TRACK_NUMBER = "TRACK_NUMBER"
    COMMENT = "COMMENT"
