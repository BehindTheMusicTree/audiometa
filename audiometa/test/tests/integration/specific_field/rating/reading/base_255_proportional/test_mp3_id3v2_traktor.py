import pytest
from pathlib import Path

from audiometa import get_unified_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.integration
class TestBase255ProportionalId3v2Mp3RatingReading:
    
    @pytest.mark.parametrize("star_rating,expected_normalized_rating", [
        (1, 20),
        (2, 40),
        (3, 60),
        (4, 80),
        (5, 100),
    ])
    def test_base_255_proportional_star_mp3_traktor(self, test_files_dir: Path, star_rating, expected_normalized_rating):
        file_path = test_files_dir / f"rating_id3v2_tracktor={star_rating} star.mp3"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is not None
        assert isinstance(rating, (int, float))
        assert rating == expected_normalized_rating

    def test_base_255_proportional_none_rating_mp3_traktor(self, test_files_dir: Path):
        file_path = test_files_dir / "rating_id3v2_tracktor=none.mp3"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        # Traktor "none" may actually be 0, not None
        assert rating is None or rating == 0
