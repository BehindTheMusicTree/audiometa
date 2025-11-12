"""Vorbis manager and constants."""

from ._vorbis_constants import (
    VORBIS_BLOCK_HEADER_SIZE,
    VORBIS_CHUNK_ID_SIZE,
    VORBIS_COMMENT_BLOCK_TYPE,
    VORBIS_ID3V2_HEADER_SIZE,
)
from ._VorbisManager import _VorbisManager

__all__ = [
    "_VorbisManager",
    "VORBIS_BLOCK_HEADER_SIZE",
    "VORBIS_CHUNK_ID_SIZE",
    "VORBIS_COMMENT_BLOCK_TYPE",
    "VORBIS_ID3V2_HEADER_SIZE",
]
