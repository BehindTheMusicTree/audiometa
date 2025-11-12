from pathlib import Path

import pytest

from audiometa import get_unified_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestBase100Proportional:
    @pytest.mark.parametrize(
        ("star_rating", "expected_normalized_rating"),
        [
            (0, 0),
            (0.5, 10),
            (1, 20),
            (1.5, 30),
            (2, 40),
            (2.5, 50),
            (3, 60),
            (3.5, 70),
            (4, 80),
            (4.5, 90),
            (5, 100),
        ],
    )
    def test_vorbis(self, assets_dir: Path, star_rating, expected_normalized_rating):
        file_path = assets_dir / f"rating_vorbis={star_rating} star.flac"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is not None
        assert isinstance(rating, int | float)
        assert rating == expected_normalized_rating

    @pytest.mark.parametrize(
        ("star_rating", "expected_normalized_rating"),
        [
            (0, 0),
            (0.5, 10),
            (1, 20),
            (1.5, 30),
            (2, 40),
            (2.5, 50),
            (3, 60),
            (3.5, 70),
            (4, 80),
            (4.5, 90),
            (5, 100),
        ],
    )
    def test_id3v2(self, assets_dir: Path, star_rating, expected_normalized_rating):
        file_path = assets_dir / f"rating_id3v2_base 100={star_rating} star.wav"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is not None
        assert isinstance(rating, int | float)
        assert rating == expected_normalized_rating

    @pytest.mark.parametrize(
        ("star_rating", "expected_normalized_rating"),
        [
            (1, 20),
            (2, 40),
            (3, 60),
            (4, 80),
            (5, 100),
        ],
    )
    def test_wav_riff(self, assets_dir: Path, star_rating, expected_normalized_rating):
        file_path = assets_dir / f"rating_riff_base 100_kid3={star_rating} star.wav"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is not None
        assert isinstance(rating, int | float)
        assert rating == expected_normalized_rating

    def test_none_rating_wav_riff(self, assets_dir: Path):
        file_path = assets_dir / "rating_riff_kid3=none.wav"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is None
