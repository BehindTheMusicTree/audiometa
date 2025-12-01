"""Unit tests for ISRC metadata field type validation."""

import pytest

from audiometa import validate_metadata_for_update
from audiometa.exceptions import InvalidMetadataFieldTypeError
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestISRCTypeValidation:
    def test_valid_isrc_string(self):
        validate_metadata_for_update({UnifiedMetadataKey.ISRC: "USRC17607839"})

    def test_valid_isrc_with_hyphens(self):
        validate_metadata_for_update({UnifiedMetadataKey.ISRC: "US-RC1-76-07839"})

    def test_invalid_isrc_type_integer_raises(self):
        with pytest.raises(InvalidMetadataFieldTypeError):
            validate_metadata_for_update({UnifiedMetadataKey.ISRC: 12345})

    def test_invalid_isrc_type_list_raises(self):
        with pytest.raises(InvalidMetadataFieldTypeError):
            validate_metadata_for_update({UnifiedMetadataKey.ISRC: ["USRC17607839"]})

    def test_isrc_none_is_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.ISRC: None})

    def test_isrc_empty_string_is_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.ISRC: ""})
