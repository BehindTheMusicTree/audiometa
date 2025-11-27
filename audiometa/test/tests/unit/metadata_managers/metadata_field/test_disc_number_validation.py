import pytest

from audiometa import validate_metadata_for_update
from audiometa.exceptions import InvalidMetadataFieldFormatError, InvalidMetadataFieldTypeError
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestDiscNumberValidation:
    """Test disc number field validation in validate_metadata_for_update."""

    @pytest.mark.parametrize(
        "disc_number",
        [1, 5, 99, 255],
    )
    def test_valid_disc_number_as_int(self, disc_number):
        validate_metadata_for_update({UnifiedMetadataKey.DISC_NUMBER: disc_number})

    @pytest.mark.parametrize(
        "disc_number",
        ["1", "5", "99"],
    )
    def test_invalid_disc_number_as_string(self, disc_number):
        with pytest.raises(InvalidMetadataFieldTypeError):
            validate_metadata_for_update({UnifiedMetadataKey.DISC_NUMBER: disc_number})

    def test_disc_number_none_is_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.DISC_NUMBER: None})

    @pytest.mark.parametrize(
        "invalid_value",
        [3.14, [], "1"],
    )
    def test_invalid_disc_number_type(self, invalid_value):
        with pytest.raises(InvalidMetadataFieldTypeError):
            validate_metadata_for_update({UnifiedMetadataKey.DISC_NUMBER: invalid_value})

    @pytest.mark.parametrize(
        "disc_number",
        [-1, -5],
    )
    def test_invalid_disc_number_negative(self, disc_number):
        with pytest.raises(InvalidMetadataFieldFormatError):
            validate_metadata_for_update({UnifiedMetadataKey.DISC_NUMBER: disc_number})


@pytest.mark.unit
class TestDiscTotalValidation:
    """Test disc total field validation in validate_metadata_for_update."""

    @pytest.mark.parametrize(
        "disc_total",
        [1, 5, 99, 255],
    )
    def test_valid_disc_total_as_int(self, disc_total):
        validate_metadata_for_update({UnifiedMetadataKey.DISC_TOTAL: disc_total})

    def test_disc_total_none_is_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.DISC_TOTAL: None})

    @pytest.mark.parametrize(
        "invalid_value",
        [3.14, [], "1"],
    )
    def test_invalid_disc_total_type(self, invalid_value):
        with pytest.raises(InvalidMetadataFieldTypeError):
            validate_metadata_for_update({UnifiedMetadataKey.DISC_TOTAL: invalid_value})

    @pytest.mark.parametrize(
        "disc_total",
        [-1, -5],
    )
    def test_invalid_disc_total_negative(self, disc_total):
        with pytest.raises(InvalidMetadataFieldFormatError):
            validate_metadata_for_update({UnifiedMetadataKey.DISC_TOTAL: disc_total})
