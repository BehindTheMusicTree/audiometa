import pytest

from audiometa import validate_metadata_for_update
from audiometa.exceptions import InvalidMetadataFieldTypeError, InvalidRatingValueError
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestRatingValidation:
    """Test rating field validation in validate_metadata_for_update."""

    @pytest.mark.parametrize(
        "rating",
        [0, 128, 255],
    )
    def test_valid_rating_raw_mode(self, rating):
        validate_metadata_for_update({UnifiedMetadataKey.RATING: rating})

    @pytest.mark.parametrize(
        "rating",
        [1.5, 75.7, 0.0],
    )
    def test_invalid_rating_float_in_raw_mode_raises_error(self, rating):
        with pytest.raises(InvalidRatingValueError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.RATING: rating})
        assert "Float values are only supported when normalized_rating_max_value is provided" in str(exc_info.value)

    @pytest.mark.parametrize(
        "rating",
        [50, 0, 100, 1.5, 7.5, 50.0],
    )
    def test_valid_rating_normalized_mode(self, rating):
        validate_metadata_for_update({UnifiedMetadataKey.RATING: rating}, normalized_rating_max_value=100)

    @pytest.mark.parametrize(
        "rating",
        [-1, -100, -0.5, -1.5],
    )
    def test_invalid_rating_negative_raises_error(self, rating):
        with pytest.raises(InvalidRatingValueError):
            validate_metadata_for_update({UnifiedMetadataKey.RATING: rating})

    @pytest.mark.parametrize(
        "rating",
        [101, 100.1, 101.5],
    )
    def test_invalid_rating_over_max_raises_error(self, rating):
        with pytest.raises(InvalidRatingValueError):
            validate_metadata_for_update({UnifiedMetadataKey.RATING: rating}, normalized_rating_max_value=100)

    @pytest.mark.parametrize(
        "rating",
        [110, 110.5],
    )
    def test_invalid_rating_profile_value_raises_error(self, rating):
        # Values > max that would map to invalid star rating indices (> 10)
        with pytest.raises(InvalidRatingValueError):
            validate_metadata_for_update({UnifiedMetadataKey.RATING: rating}, normalized_rating_max_value=100)

    @pytest.mark.parametrize(
        "invalid_value",
        ["invalid", {}],
    )
    def test_invalid_rating_type_raises_error(self, invalid_value):
        with pytest.raises(InvalidMetadataFieldTypeError):
            validate_metadata_for_update({UnifiedMetadataKey.RATING: invalid_value})

    def test_rating_none_is_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.RATING: None})
