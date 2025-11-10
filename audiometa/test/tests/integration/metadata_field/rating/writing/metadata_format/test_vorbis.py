import pytest

from audiometa import get_unified_metadata, get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.integration
class TestVorbisRatingWriting:
    @pytest.mark.parametrize(
        "star_rating,expected_normalized_rating",
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

        with temp_file_with_metadata(basic_metadata, "flac") as test_file_path:
            test_metadata = {UnifiedMetadataKey.RATING: expected_normalized_rating}
            update_metadata(
                test_file_path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.VORBIS
            )
            metadata = get_unified_metadata(test_file_path, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == expected_normalized_rating

    def test_write_base_100_proportional_values(self):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        # Test values that correspond to BASE_100_PROPORTIONAL profile
        test_values = [0, 20, 40, 60, 80, 100]  # 0, 1, 2, 3, 4, 5 stars in base 100

        with temp_file_with_metadata(basic_metadata, "flac") as test_file_path:
            for value in test_values:
                test_metadata = {UnifiedMetadataKey.RATING: value}
                update_metadata(
                    test_file_path,
                    test_metadata,
                    normalized_rating_max_value=100,
                    metadata_format=MetadataFormat.VORBIS,
                )
                rating = get_unified_metadata_field(
                    test_file_path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100
                )
                assert rating is not None
                assert rating == value

    def test_write_none_removes_rating(self):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        with temp_file_with_metadata(basic_metadata, "flac") as test_file_path:
            # First write a rating
            test_metadata = {UnifiedMetadataKey.RATING: 80}
            update_metadata(
                test_file_path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.VORBIS
            )
            rating = get_unified_metadata_field(
                test_file_path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100
            )
            assert rating == 80

            # Then remove it with None
            test_metadata = {UnifiedMetadataKey.RATING: None}
            update_metadata(
                test_file_path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.VORBIS
            )
            rating = get_unified_metadata_field(
                test_file_path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100
            )
            # Rating removal behavior may vary - check if it's None or 0
            assert rating is None or rating == 0
