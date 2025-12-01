"""Unit tests for ISRC metadata field format validation."""

import pytest

from audiometa import validate_metadata_for_update
from audiometa.exceptions import InvalidMetadataFieldFormatError, InvalidMetadataFieldTypeError
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestISRCFormatValidation:
    @pytest.mark.parametrize(
        "isrc",
        [
            "USRC17607839",  # Standard 12-char format
            "GBAYE0000001",  # UK code
            "JPAB01234567",  # Japan code
            "DEAB01234567",  # Germany code
            "usrc17607839",  # Lowercase allowed
            "UsRc17607839",  # Mixed case allowed
        ],
    )
    def test_valid_12_char_format(self, isrc):
        validate_metadata_for_update({UnifiedMetadataKey.ISRC: isrc})

    @pytest.mark.parametrize(
        "isrc",
        [
            "US-RC1-76-07839",  # Standard hyphenated format
            "GB-AYE-00-00001",  # UK code with hyphens
            "JP-AB0-12-34567",  # Japan code with hyphens
        ],
    )
    def test_valid_hyphenated_format(self, isrc):
        validate_metadata_for_update({UnifiedMetadataKey.ISRC: isrc})

    @pytest.mark.parametrize(
        "isrc",
        [
            "USRC1760783",  # Too short (11 chars)
            "USRC176078",  # Too short (10 chars)
            "USRC17607",  # Too short (9 chars)
            "ABC",  # Way too short
            "U",  # Single char
        ],
    )
    def test_invalid_format_too_short(self, isrc):
        with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.ISRC: isrc})
        error = exc_info.value
        assert error.field == UnifiedMetadataKey.ISRC.value
        assert error.value == isrc
        assert "12 alphanumeric characters" in error.expected_format

    @pytest.mark.parametrize(
        "isrc",
        [
            "USRC176078390",  # Too long (13 chars)
            "USRC1760783901",  # Too long (14 chars)
            "USRC17607839012",  # Too long (15 chars non-hyphenated)
            "USRC176078390123",  # Too long (16 chars)
        ],
    )
    def test_invalid_format_too_long(self, isrc):
        with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.ISRC: isrc})
        error = exc_info.value
        assert error.field == UnifiedMetadataKey.ISRC.value
        assert error.value == isrc
        assert "12 alphanumeric characters" in error.expected_format

    @pytest.mark.parametrize(
        "isrc",
        [
            "USRC-17607839",  # Wrong hyphen position
            "US-RC17607839",  # Missing hyphens
            "US-RC1-7607839",  # Wrong segment lengths
            "US-RC1-76-0783",  # Last segment too short (4 chars)
            "US-RC1-76-078390",  # Last segment too long (6 chars)
            "US-R-76-07839",  # Second segment too short
            "US-RC12-76-07839",  # Second segment too long
            "U-RC1-76-07839",  # First segment too short
            "USA-RC1-76-07839",  # First segment too long
            "US-RC1-7-07839",  # Third segment too short
            "US-RC1-761-07839",  # Third segment too long
        ],
    )
    def test_invalid_hyphenated_format(self, isrc):
        with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.ISRC: isrc})
        error = exc_info.value
        assert error.field == UnifiedMetadataKey.ISRC.value
        assert error.value == isrc

    @pytest.mark.parametrize(
        "isrc",
        [
            "USRC1760783!",  # Special character
            "USRC@7607839",  # Special character
            "USRC 7607839",  # Space
            "USRC_7607839",  # Underscore
        ],
    )
    def test_invalid_format_special_characters(self, isrc):
        with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.ISRC: isrc})
        error = exc_info.value
        assert error.field == UnifiedMetadataKey.ISRC.value
        assert error.value == isrc

    def test_none_value_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.ISRC: None})

    def test_empty_string_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.ISRC: ""})

    def test_format_validation_after_type_validation(self):
        invalid_type = {UnifiedMetadataKey.ISRC: 12345}
        with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
            validate_metadata_for_update(invalid_type)
        assert not isinstance(exc_info.value, InvalidMetadataFieldFormatError)
