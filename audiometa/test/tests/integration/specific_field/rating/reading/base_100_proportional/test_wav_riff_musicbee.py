import pytest
from pathlib import Path

from audiometa import get_unified_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.integration
class TestBase100ProportionalRiffWavRatingReading:
    
    @pytest.mark.parametrize("star_rating,expected_normalized_rating", [
        (1, 20),
        (2, 40),
        (3, 60),
        (4, 80),
        (5, 100),
    ])
    def test_base_100_proportional_star_wav_riff(self, test_files_dir: Path, star_rating, expected_normalized_rating):
        file_path = test_files_dir / f"rating_riff_base 100_kid3={star_rating} star.wav"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is not None
        assert isinstance(rating, (int, float))
        assert rating == expected_normalized_rating

    def test_base_100_proportional_none_rating_wav_riff(self, test_files_dir: Path):
        file_path = test_files_dir / "rating_riff_kid3=none.wav"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is None
