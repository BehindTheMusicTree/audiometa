"""Tests for unified metadata field schema helpers."""

import pytest

from audiometa import UnifiedMetadataKey, get_unified_metadata_field_schema
from audiometa.utils.unified_metadata_field_schema import describe_unified_metadata_field


def _expected_value_shape(key: UnifiedMetadataKey) -> tuple[str, bool, bool]:
    if key.can_semantically_have_multiple_values():
        return ("strings", True, False)
    if key == UnifiedMetadataKey.TRACK_NUMBER:
        return ("string_or_integer", False, False)
    if key in (UnifiedMetadataKey.DISC_NUMBER, UnifiedMetadataKey.DISC_TOTAL):
        return ("integer", False, True)
    if key == UnifiedMetadataKey.RATING:
        return ("number", False, False)
    opt = key.get_optional_type()
    if opt is str:
        return ("string", False, False)
    if opt is int:
        return ("integer", False, False)
    return ("string", False, False)


@pytest.mark.unit
class TestUnifiedMetadataFieldSchema:
    def test_schema_covers_all_enum_members(self) -> None:
        schema = get_unified_metadata_field_schema()
        ids = {entry["id"] for entry in schema}
        assert ids == {k.value for k in UnifiedMetadataKey}

    def test_each_descriptor_keys_and_id_match_enum(self) -> None:
        required = {"id", "label", "multiple", "value_type", "optional_value"}
        for key in UnifiedMetadataKey:
            d = describe_unified_metadata_field(key)
            assert set(d.keys()) == required
            assert d["id"] == key.value
            assert isinstance(d["label"], str)
            assert d["label"]
            assert isinstance(d["multiple"], bool)
            assert isinstance(d["value_type"], str)
            assert d["value_type"]
            assert isinstance(d["optional_value"], bool)

    def test_each_descriptor_value_shape_matches_contract(self) -> None:
        for key in UnifiedMetadataKey:
            d = describe_unified_metadata_field(key)
            vt, mult, optv = _expected_value_shape(key)
            assert d["value_type"] == vt
            assert d["multiple"] is mult
            assert d["optional_value"] is optv

    def test_describe_title_scalar_string(self) -> None:
        d = describe_unified_metadata_field(UnifiedMetadataKey.TITLE)
        assert d["id"] == "title"
        assert d["label"] == "Title"
        assert d["multiple"] is False
        assert d["value_type"] == "string"
        assert d["optional_value"] is False

    def test_describe_artists_multi_strings(self) -> None:
        d = describe_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
        assert d["multiple"] is True
        assert d["value_type"] == "strings"

    def test_describe_track_number_string_or_integer(self) -> None:
        d = describe_unified_metadata_field(UnifiedMetadataKey.TRACK_NUMBER)
        assert d["value_type"] == "string_or_integer"
        assert d["multiple"] is False
        assert d["optional_value"] is False

    def test_describe_disc_number_integer_optional_value(self) -> None:
        d = describe_unified_metadata_field(UnifiedMetadataKey.DISC_NUMBER)
        assert d["value_type"] == "integer"
        assert d["optional_value"] is True
        assert d["multiple"] is False

    def test_describe_disc_total_integer_optional_value(self) -> None:
        d = describe_unified_metadata_field(UnifiedMetadataKey.DISC_TOTAL)
        assert d["value_type"] == "integer"
        assert d["optional_value"] is True
        assert d["multiple"] is False

    def test_describe_rating_number(self) -> None:
        d = describe_unified_metadata_field(UnifiedMetadataKey.RATING)
        assert d["value_type"] == "number"
        assert d["multiple"] is False
        assert d["optional_value"] is False

    def test_describe_bpm_integer_scalar(self) -> None:
        d = describe_unified_metadata_field(UnifiedMetadataKey.BPM)
        assert d["value_type"] == "integer"
        assert d["optional_value"] is False
