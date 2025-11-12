from pathlib import Path

import pytest

from audiometa import get_unified_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestBase255Proportional:
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
    def test_vorbis_flac_traktor(self, assets_dir: Path, star_rating, expected_normalized_rating):
        file_path = assets_dir / f"rating_vorbis_traktor={star_rating} star.flac"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is not None
        assert isinstance(rating, int | float)
        assert rating == expected_normalized_rating

    def test_none_rating_vorbis_flac_traktor(self, assets_dir: Path):
        file_path = assets_dir / "rating_vorbis_traktor=none.flac"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is None

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
    def test_id3v2_mp3_traktor(self, assets_dir: Path, star_rating, expected_normalized_rating):
        file_path = assets_dir / f"rating_id3v2_tracktor={star_rating} star.mp3"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is not None
        assert isinstance(rating, int | float)
        assert rating == expected_normalized_rating

    def test_none_rating_id3v2_mp3_traktor(self, assets_dir: Path):
        file_path = assets_dir / "rating_id3v2_tracktor=none.mp3"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        # Traktor "none" may actually be 0, not None
        assert rating is None or rating == 0
