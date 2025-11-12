from pathlib import Path

import pytest

from audiometa import get_unified_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestBase255NonProportional:
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
    def test_id3v2_mp3(self, assets_dir: Path, star_rating, expected_normalized_rating):
        file_path = assets_dir / f"rating_id3v2={star_rating} star.mp3"
        metadata = get_unified_metadata(file_path, normalized_rating_max_value=100)
        rating = metadata.get(UnifiedMetadataKey.RATING)
        assert rating is not None
        assert isinstance(rating, int | float)
        assert rating == expected_normalized_rating
