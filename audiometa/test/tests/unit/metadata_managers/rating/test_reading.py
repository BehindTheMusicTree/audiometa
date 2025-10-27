
import pytest

from audiometa.utils.rating_profiles import RatingReadProfile
from audiometa.manager.rating_supporting.RatingSupportingMetadataManager import RatingSupportingMetadataManager


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
    def test_base_255_non_proportional(self, mocker, metadata_rating_read, expected_normalized_value):
        mock_raw_metadata = mocker.MagicMock()
        mock_raw_metadata.tags = {'rating': metadata_rating_read}
        mocker.patch.object(RatingSupportingMetadataManager, '_extract_mutagen_metadata', return_value=mock_raw_metadata)
        manager = RatingSupportingMetadataManager(
            audio_file=mocker.MagicMock(),
            metadata_keys_direct_map_read={'rating': 'rating'},)
        assert manager.get_unified_metadata_field('rating') == expected_normalized_value
            