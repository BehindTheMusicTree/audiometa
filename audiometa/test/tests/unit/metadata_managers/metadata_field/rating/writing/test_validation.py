from unittest.mock import MagicMock

import pytest

from audiometa.exceptions import InvalidRatingValueError
from audiometa.manager._rating_supporting.id3v2._Id3v2Manager import _Id3v2Manager as Id3v2Manager
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.unit
class TestRatingValidation:
    def test_validate_rating_value_raw_mode_non_negative_allowed(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=None)

        # These should not raise any exceptions
        manager._validate_rating_value(0)
        manager._validate_rating_value(1)
        manager._validate_rating_value(128)
        manager._validate_rating_value(255)
        manager._validate_rating_value(1000)

    def test_validate_rating_value_raw_mode_negative_rejected(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=None)

        with pytest.raises(InvalidRatingValueError) as exc_info:
            manager._validate_rating_value(-1)
        assert "must be non-negative" in str(exc_info.value)

        with pytest.raises(InvalidRatingValueError) as exc_info:
            manager._validate_rating_value(-100)
        assert "must be non-negative" in str(exc_info.value)

    def test_validate_rating_value_normalized_mode_valid_values(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        # Valid values: those that map to BASE_100_PROPORTIONAL profile
        # (value/100 * 100) must be in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        valid_values = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        for value in valid_values:
            manager._validate_rating_value(value)

    def test_validate_rating_value_normalized_mode_negative_rejected(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        with pytest.raises(InvalidRatingValueError) as exc_info:
            manager._validate_rating_value(-1)
        assert "must be non-negative" in str(exc_info.value)

    def test_validate_rating_value_normalized_mode_over_max_rejected(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        with pytest.raises(InvalidRatingValueError) as exc_info:
            manager._validate_rating_value(101)
        assert "out of range" in str(exc_info.value)
        assert "must be between 0 and 100" in str(exc_info.value)

    def test_validate_rating_value_normalized_mode_invalid_profile_value(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=100)

        # 33/100 * 100 = 33, which is not in BASE_100_PROPORTIONAL
        # 33/100 * 255 = 84, which is not in BASE_255_NON_PROPORTIONAL
        with pytest.raises(InvalidRatingValueError) as exc_info:
            manager._validate_rating_value(33)
        assert "do not exist in any supported writing profile" in str(exc_info.value)

    def test_validate_rating_value_normalized_mode_different_max_values(self):
        """Test profile-based validation with different max values."""
        # Test with max_value = 10 (0-10 scale)
        manager_10 = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=10)
        # All values 0-10 map to valid profile values
        valid_values_10 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for value in valid_values_10:
            manager_10._validate_rating_value(value)

        # Test with max_value = 255
        manager_255 = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=255)
        # Valid values: those that map to BASE_255_NON_PROPORTIONAL profile values
        # BASE_255_NON_PROPORTIONAL = [0, 13, 1, 54, 64, 118, 128, 186, 196, 242, 255]
        # So valid normalized values are: 0, 13, 1, 54, 64, 118, 128, 186, 196, 242, 255
        valid_values_255 = [0, 1, 13, 54, 64, 118, 128, 186, 196, 242, 255]
        for value in valid_values_255:
            manager_255._validate_rating_value(value)

        # Also valid: values that map to BASE_100_PROPORTIONAL when scaled
        # For example: 50/255 * 100 = 20 (round), which is in BASE_100_PROPORTIONAL
        valid_values_255_also_100 = [25, 50, 76, 102, 127, 153, 178, 204, 229]
        for value in valid_values_255_also_100:
            manager_255._validate_rating_value(value)

        # Invalid: values that don't map to any profile
        # 37/255 * 100 = 15 (round), not in BASE_100_PROPORTIONAL
        # 37/255 * 255 = 37 (round), not in BASE_255_NON_PROPORTIONAL
        invalid_values_255 = [37, 99, 200]
        for value in invalid_values_255:
            with pytest.raises(InvalidRatingValueError) as exc_info:
                manager_255._validate_rating_value(value)
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
