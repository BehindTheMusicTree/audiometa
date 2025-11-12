"""Type definitions for audio metadata handling.

This module contains type aliases and enums used throughout the application for representing raw and unified metadata
values.
"""

from collections.abc import MutableMapping
from enum import Enum
from typing import Any, TypedDict

from .unified_metadata_key import UnifiedMetadataKey


class RawMetadataKey(str, Enum):
    """Enumeration of raw metadata keys."""

    def __str__(self) -> str:
        """Return string representation of the key."""
        return str(self.value)


"""
Raw metadata value can be none (when not set), string (title), integer (rating), float(BPM) or list[str] (artists
names).
"""
UnifiedMetadataValue = int | float | str | list[str] | None
RawMetadataValue = list[int] | list[float] | list[str] | None
RawMetadataDict = dict[RawMetadataKey, RawMetadataValue]
UnifiedMetadata = MutableMapping[UnifiedMetadataKey, UnifiedMetadataValue]


class FormatPriorities(TypedDict):
    """Type for format priorities information."""

    file_extension: str
    reading_order: list[str]
    writing_format: str | None


class TechnicalInfo(TypedDict):
    """Type for technical audio information."""

    duration_seconds: float
    bitrate_kbps: int
    sample_rate_hz: int
    channels: int
    file_size_bytes: int
    file_extension: str
    audio_format_name: str
    is_flac_md5_valid: bool | None


class HeaderInfo(TypedDict):
    """Type for format-specific header information."""

    present: bool
    version: str | None
    size_bytes: int
    position: int | None
    flags: dict[str, Any]
    extended_header: dict[str, Any]


class RawMetadataInfo(TypedDict):
    """Type for raw metadata information."""

    raw_data: Any
    parsed_fields: dict[str, Any]
    frames: dict[str, Any]
    comments: dict[str, Any]
    chunk_structure: dict[str, Any]


class FullMetadata(TypedDict):
    """Type for comprehensive metadata returned by get_full_metadata."""

    unified_metadata: UnifiedMetadata
    technical_info: TechnicalInfo
    metadata_format: dict[str, UnifiedMetadata]
    headers: dict[str, HeaderInfo]
    raw_metadata: dict[str, RawMetadataInfo]
    format_priorities: FormatPriorities
