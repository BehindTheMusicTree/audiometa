"""Wire-oriented schema for unified metadata fields (API / UI).

Describes every :class:`UnifiedMetadataKey` with stable ids (enum values), human labels,
and value shape hints. Format-specific mapping stays in metadata managers.
"""

from __future__ import annotations

from typing import Any

from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

# Stable English labels for clients that do not localize.
_UNIFIED_METADATA_LABELS: dict[UnifiedMetadataKey, str] = {
    UnifiedMetadataKey.TITLE: "Title",
    UnifiedMetadataKey.ARTISTS: "Artists",
    UnifiedMetadataKey.ALBUM: "Album",
    UnifiedMetadataKey.ALBUM_ARTISTS: "Album artists",
    UnifiedMetadataKey.GENRES_NAMES: "Genres",
    UnifiedMetadataKey.RATING: "Rating",
    UnifiedMetadataKey.LANGUAGE: "Language",
    UnifiedMetadataKey.RELEASE_DATE: "Release date",
    UnifiedMetadataKey.TRACK_NUMBER: "Track number",
    UnifiedMetadataKey.DISC_NUMBER: "Disc number",
    UnifiedMetadataKey.DISC_TOTAL: "Total discs",
    UnifiedMetadataKey.BPM: "BPM",
    UnifiedMetadataKey.COMPOSERS: "Composers",
    UnifiedMetadataKey.PUBLISHER: "Publisher",
    UnifiedMetadataKey.COPYRIGHT: "Copyright",
    UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: "Lyrics (unsynchronized)",
    UnifiedMetadataKey.COMMENT: "Comment",
    UnifiedMetadataKey.REPLAYGAIN: "ReplayGain",
    UnifiedMetadataKey.ARCHIVAL_LOCATION: "Archival location",
    UnifiedMetadataKey.ISRC: "ISRC",
    UnifiedMetadataKey.MUSICBRAINZ_TRACKID: "MusicBrainz recording ID",
    UnifiedMetadataKey.MUSICBRAINZ_ARTISTIDS: "MusicBrainz artist IDs",
    UnifiedMetadataKey.DESCRIPTION: "Description",
    UnifiedMetadataKey.ORIGINATOR: "Originator",
}

# value_type is a coarse JSON-oriented hint for forms.
# - strings: list of strings
# - string, integer, number: scalar
# - string_or_integer: track number (library accepts int or str on write)
# integer with optional_value=True: may be null (e.g. disc total)
_VALUE_SHAPE: dict[UnifiedMetadataKey, tuple[str, bool, bool]] = {}
for _k in UnifiedMetadataKey:
    if _k.can_semantically_have_multiple_values():
        _VALUE_SHAPE[_k] = ("strings", True, False)
    elif _k == UnifiedMetadataKey.TRACK_NUMBER:
        _VALUE_SHAPE[_k] = ("string_or_integer", False, False)
    elif _k in (UnifiedMetadataKey.DISC_NUMBER, UnifiedMetadataKey.DISC_TOTAL):
        _VALUE_SHAPE[_k] = ("integer", False, True)
    elif _k == UnifiedMetadataKey.RATING:
        _VALUE_SHAPE[_k] = ("number", False, False)
    else:
        _opt = _k.get_optional_type()
        if _opt is str:
            _VALUE_SHAPE[_k] = ("string", False, False)
        elif _opt is int:
            _VALUE_SHAPE[_k] = ("integer", False, False)
        else:
            _VALUE_SHAPE[_k] = ("string", False, False)


def describe_unified_metadata_field(key: UnifiedMetadataKey) -> dict[str, Any]:
    """Single field descriptor for APIs."""
    value_type, multiple, optional_value = _VALUE_SHAPE[key]
    return {
        "id": key.value,
        "label": _UNIFIED_METADATA_LABELS[key],
        "multiple": multiple,
        "value_type": value_type,
        "optional_value": optional_value,
    }


def get_unified_metadata_field_schema() -> list[dict[str, Any]]:
    """Return descriptors for all unified metadata keys (library vocabulary)."""
    return [describe_unified_metadata_field(k) for k in UnifiedMetadataKey]
