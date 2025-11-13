import pytest

from audiometa import validate_metadata_for_update
from audiometa.exceptions import InvalidMetadataFieldFormatError, InvalidMetadataFieldTypeError
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestTrackNumberValidation:
    """Test track number field validation in validate_metadata_for_update."""

    @pytest.mark.parametrize(
        "track_number",
        [1, 5, 99],
    )
    def test_valid_track_number_as_int(self, track_number):
        validate_metadata_for_update({UnifiedMetadataKey.TRACK_NUMBER: track_number})

    @pytest.mark.parametrize(
        "track_number",
        ["1", "5", "99"],
    )
    def test_valid_track_number_as_string(self, track_number):
        validate_metadata_for_update({UnifiedMetadataKey.TRACK_NUMBER: track_number})

    @pytest.mark.parametrize(
        "track_number",
        ["5/12", "1/10", "99/100"],
    )
    def test_valid_track_number_with_total(self, track_number):
        validate_metadata_for_update({UnifiedMetadataKey.TRACK_NUMBER: track_number})

    def test_invalid_track_number_format(self):
        with pytest.raises(InvalidMetadataFieldFormatError):
            validate_metadata_for_update({UnifiedMetadataKey.TRACK_NUMBER: "/12"})

    def test_track_number_none_is_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.TRACK_NUMBER: None})

    @pytest.mark.parametrize(
        "invalid_value",
        [3.14, []],
    )
    def test_invalid_track_number_type(self, invalid_value):
        with pytest.raises(InvalidMetadataFieldTypeError):
            validate_metadata_for_update({UnifiedMetadataKey.TRACK_NUMBER: invalid_value})
