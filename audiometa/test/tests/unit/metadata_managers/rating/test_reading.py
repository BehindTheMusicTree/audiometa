

import pytest
from unittest.mock import MagicMock

from audiometa.utils.rating_profiles import RatingReadProfile
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.manager.rating_supporting.Id3v2Manager import Id3v2Manager


@pytest.mark.unit
class TestRatingProfileValues:
    
    
    @pytest.mark.parametrize("profile_enum, expected_values", [
        (RatingReadProfile.BASE_255_NON_PROPORTIONAL, [0, 13, 1, 54, 64, 118, 128, 186, 196, 242, 255]),
        (RatingReadProfile.BASE_100_PROPORTIONAL, [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
        (RatingReadProfile.BASE_255_PROPORTIONAL, [None, None, 51, None, 102, None, 153, None, 204, None, 255]),
    ])
    def test_profile_values(self, profile_enum, expected_values):
        profile = profile_enum.value
        
        assert profile == expected_values
        assert len(profile) == 11  # 0-5 stars (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)

    @pytest.mark.parametrize("metadata_rating_read, expected_normalized_value", [
        (0, 0),
        (13, 1),
        (1, 2),
        (54, 3),
        (64, 4),
        (118, 5),
        (128, 6),
        (186, 7),
        (196, 8),
        (242, 9),
        (255, 10),
    ])
    def test_base_255_non_proportional(self, metadata_rating_read, expected_normalized_value):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=10)
        normalized_rating = manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={Id3v2Manager.Id3TextFrame.RATING: [manager.ID3_RATING_APP_EMAIL, metadata_rating_read]},
        )
        assert normalized_rating == expected_normalized_value
        
    @pytest.mark.parametrize("metadata_rating_read, expected_normalized_value", [
        (0, 0),
        (10, 1),
        (20, 2),
        (30, 3),
        (40, 4),
        (50, 5),
        (60, 6),
        (70, 7),
        (80, 8),
        (90, 9),
        (100, 10),
    ])
    def test_base_100_proportional(self, metadata_rating_read, expected_normalized_value):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=10)
        normalized_rating = manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={Id3v2Manager.Id3TextFrame.RATING: [manager.ID3_RATING_APP_EMAIL, metadata_rating_read]},
        )
        assert normalized_rating == expected_normalized_value
        
    @pytest.mark.parametrize("metadata_rating_read, expected_normalized_value", [
        (51, 1),
        (102, 2),
        (153, 3),
        (204, 4),
        (255, 5),
    ])
    def test_base_255_proportional(self, metadata_rating_read, expected_normalized_value):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=5)
        normalized_rating = manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={Id3v2Manager.Id3TextFrame.RATING: [manager.ID3_RATING_APP_EMAIL, metadata_rating_read]},
        )
        assert normalized_rating == expected_normalized_value
        
    def test_invalid_value(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=10)
        normalized_rating = manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={Id3v2Manager.Id3TextFrame.RATING: [manager.ID3_RATING_APP_EMAIL, 300]},
        )
        assert normalized_rating is None
