from unittest.mock import MagicMock

import pytest

from audiometa.exceptions import InvalidRatingValueError
from audiometa.manager._rating_supporting._RatingSupportingMetadataManager import (
    _RatingSupportingMetadataManager,
)
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

    def test_validate_rating_value_raw_mode_negative_rejected(self):
        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(-1, None)
        assert "must be non-negative" in str(exc_info.value)

        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(-100, None)
        assert "must be non-negative" in str(exc_info.value)

    def test_validate_rating_value_normalized_mode_valid_values(self):
        # Valid values: those that map to BASE_100_PROPORTIONAL profile
        # (value/100 * 100) must be in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        valid_values = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        for value in valid_values:
            _RatingSupportingMetadataManager.validate_rating_value(value, 100)

    def test_validate_rating_value_normalized_mode_negative_rejected(self):
        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(-1, 100)
        assert "must be non-negative" in str(exc_info.value)

    def test_validate_rating_value_normalized_mode_over_max_rejected(self):
        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(101, 100)
        assert "out of range" in str(exc_info.value)
        assert "must be between 0 and 100" in str(exc_info.value)

    def test_validate_rating_value_normalized_mode_invalid_profile_value(self):
        # 33/100 * 100 = 33, which is not in BASE_100_PROPORTIONAL
        # 33/100 * 255 = 84, which is not in BASE_255_NON_PROPORTIONAL
        with pytest.raises(InvalidRatingValueError) as exc_info:
            _RatingSupportingMetadataManager.validate_rating_value(33, 100)
        assert "do not exist in any supported writing profile" in str(exc_info.value)

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

        # Invalid: values that don't map to any profile
        # 37/255 * 100 = 15 (round), not in BASE_100_PROPORTIONAL
        # 37/255 * 255 = 37 (round), not in BASE_255_NON_PROPORTIONAL
        invalid_values_255 = [37, 99, 200]
        for value in invalid_values_255:
            with pytest.raises(InvalidRatingValueError) as exc_info:
                _RatingSupportingMetadataManager.validate_rating_value(value, 255)
            assert "do not exist in any supported writing profile" in str(exc_info.value)

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

    def test_validate_rating_in_unified_metadata_float_converted(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        # Float should be accepted (converted to int internally)
        manager._validate_rating_in_unified_metadata({UnifiedMetadataKey.RATING: 50.0})

    def test_validate_rating_in_unified_metadata_none_ignored(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        # None should be ignored (no exception)
        manager._validate_rating_in_unified_metadata({UnifiedMetadataKey.RATING: None})

    def test_validate_rating_in_unified_metadata_missing_key(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        # Missing key should be ignored
        manager._validate_rating_in_unified_metadata({})
