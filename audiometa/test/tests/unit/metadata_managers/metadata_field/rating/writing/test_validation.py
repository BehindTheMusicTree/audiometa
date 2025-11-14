from unittest.mock import MagicMock

import pytest

from audiometa.exceptions import InvalidRatingValueError
from audiometa.manager._rating_supporting._RatingSupportingMetadataManager import _RatingSupportingMetadataManager
from audiometa.manager._rating_supporting.id3v2._Id3v2Manager import _Id3v2Manager as Id3v2Manager
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestRatingValidation:
    def test_validate_rating_value_raw_mode_non_negative_allowed(self):
        # These should not raise any exceptions
        _RatingSupportingMetadataManager.validate_rating_value(0, None)
        _RatingSupportingMetadataManager.validate_rating_value(1, None)
        _RatingSupportingMetadataManager.validate_rating_value(128, None)
        _RatingSupportingMetadataManager.validate_rating_value(255, None)
        _RatingSupportingMetadataManager.validate_rating_value(1000, None)
        _RatingSupportingMetadataManager.validate_rating_value(1.5, None)
        _RatingSupportingMetadataManager.validate_rating_value(75.7, None)
        _RatingSupportingMetadataManager.validate_rating_value(0.0, None)

    def test_validate_rating_value_raw_mode_negative_rejected(self):
        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(-1, None)
        assert "must be non-negative" in str(exc_info.value)

        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(-100, None)
        assert "must be non-negative" in str(exc_info.value)

        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(-0.5, None)
        assert "must be non-negative" in str(exc_info.value)

    def test_validate_rating_value_normalized_mode_valid_values(self):
        # Valid values: those that map to BASE_100_PROPORTIONAL profile
        # (value/100 * 100) must be in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        valid_values = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        for value in valid_values:
            _RatingSupportingMetadataManager.validate_rating_value(value, 100)

    def test_validate_rating_value_normalized_mode_valid_float_values(self):
        # Valid float values: 1.5/10 * 100 = 15 (in BASE_100_PROPORTIONAL)
        _RatingSupportingMetadataManager.validate_rating_value(1.5, 10)
        # 2.5/10 * 100 = 25 (in BASE_100_PROPORTIONAL)
        _RatingSupportingMetadataManager.validate_rating_value(2.5, 10)
        # 7.5/10 * 100 = 75 (in BASE_100_PROPORTIONAL)
        _RatingSupportingMetadataManager.validate_rating_value(7.5, 10)
        # 50.0/100 * 100 = 50 (in BASE_100_PROPORTIONAL)
        _RatingSupportingMetadataManager.validate_rating_value(50.0, 100)

    def test_validate_rating_value_normalized_mode_negative_rejected(self):
        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(-1, 100)
        assert "must be non-negative" in str(exc_info.value)

    @pytest.mark.parametrize(
        "rating",
        [101, 100.1, 101.5],
    )
    def test_validate_rating_value_normalized_mode_over_max_rejected(self, rating):
        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(rating, 100)
        assert "out of range" in str(exc_info.value)
        assert "must be between 0 and 100" in str(exc_info.value)

    def test_validate_rating_value_normalized_mode_invalid_profile_value(self):
        # 33/100 maps to star rating index 3 (1.5 stars), which is valid
        # This test verifies that values mapping to valid star rating indices are accepted
        # Note: The old validation checked if output values exist, but the conversion uses star rating indices
        _RatingSupportingMetadataManager.validate_rating_value(33, 100)

        # Test a value that would map to an invalid star rating index (> 10)
        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(110, 100)
        assert "out of range" in str(exc_info.value)

    def test_validate_rating_value_normalized_mode_different_max_values(self):
        """Test profile-based validation with different max values."""
        # Test with max_value = 10 (0-10 scale)
        # All values 0-10 map to valid profile values
        valid_values_10 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for value in valid_values_10:
            _RatingSupportingMetadataManager.validate_rating_value(value, 10)

        # Test with max_value = 255
        # Valid values: those that map to BASE_255_NON_PROPORTIONAL profile values
        # Profile values: 0, 13, 1, 54, 64, 118, 128, 186, 196, 242, 255
        # So valid normalized values are: 0, 13, 1, 54, 64, 118, 128, 186, 196, 242, 255
        valid_values_255 = [0, 1, 13, 54, 64, 118, 128, 186, 196, 242, 255]
        for value in valid_values_255:
            _RatingSupportingMetadataManager.validate_rating_value(value, 255)

        # Also valid: values that map to BASE_100_PROPORTIONAL when scaled
        # For example: 50/255 * 100 = 20 (round), which is in BASE_100_PROPORTIONAL
        valid_values_255_also_100 = [25, 50, 76, 102, 127, 153, 178, 204, 229]
        for value in valid_values_255_also_100:
            _RatingSupportingMetadataManager.validate_rating_value(value, 255)

        # Values that map to valid star rating indices are accepted
        # The conversion uses star rating indices (0-10), not direct output values
        # 37/255 -> index 1 (0.5 stars) -> valid
        # 99/255 -> index 4 (2 stars) -> valid
        # 200/255 -> index 8 (4 stars) -> valid
        # All these values map to valid star rating indices, so they are accepted

        # Test a value that would map to an invalid star rating index (> 10)
        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(256, 255)
        assert "out of range" in str(exc_info.value)

    def test_validate_rating_in_unified_metadata_valid(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        # Valid metadata should not raise
        manager._validate_rating_in_unified_metadata({UnifiedMetadataKey.RATING: 50})

    def test_validate_rating_in_unified_metadata_invalid_type(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        # String should raise InvalidRatingValueError
        with pytest.raises(InvalidRatingValueError) as exc_info:
            manager._validate_rating_in_unified_metadata({UnifiedMetadataKey.RATING: "invalid"})
        assert "Rating value must be numeric" in str(exc_info.value)

        # Dict should raise InvalidRatingValueError
        with pytest.raises(InvalidRatingValueError) as exc_info:
            manager._validate_rating_in_unified_metadata({UnifiedMetadataKey.RATING: {"not": "valid"}})
        assert "Rating value must be numeric" in str(exc_info.value)

    def test_validate_rating_in_unified_metadata_float_accepted(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        # Float should be accepted
        manager._validate_rating_in_unified_metadata({UnifiedMetadataKey.RATING: 50.0})
        manager._validate_rating_in_unified_metadata({UnifiedMetadataKey.RATING: 1.5})
        manager._validate_rating_in_unified_metadata({UnifiedMetadataKey.RATING: 7.5})

    def test_validate_rating_in_unified_metadata_none_ignored(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        # None should be ignored (no exception)
        manager._validate_rating_in_unified_metadata({UnifiedMetadataKey.RATING: None})

    def test_validate_rating_in_unified_metadata_missing_key(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        # Missing key should be ignored
        manager._validate_rating_in_unified_metadata({})
