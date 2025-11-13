import pytest

from audiometa import get_unified_metadata, get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestVorbisRatingWriting:
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
    def test_write_star_rating(self, star_rating, expected_normalized_rating):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        with temp_file_with_metadata(basic_metadata, "flac") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: star_rating}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=5, metadata_format=MetadataFormat.VORBIS
            )
            metadata = get_unified_metadata(test_file)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating == expected_normalized_rating

    def test_write_none_removes_rating(self):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        with temp_file_with_metadata(basic_metadata, "flac") as test_file:
            # First write a rating
            test_metadata = {UnifiedMetadataKey.RATING: 80}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.VORBIS
            )
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating == 80

            # Then remove it with None
            test_metadata = {UnifiedMetadataKey.RATING: None}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.VORBIS
            )
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating is None
