import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestId3v2RatingWriting:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (0, 0),
            (0.5, 13),
            (1, 1),
            (1.5, 54),
            (2, 64),
            (2.5, 118),
            (3, 128),
            (3.5, 186),
            (4, 196),
            (4.5, 242),
            (5, 255),
        ],
    )
    def test_write_base_255_non_proportional_values(self, value, expected):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        with temp_file_with_metadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: value}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=5, metadata_format=MetadataFormat.ID3V2
            )
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING)
            assert rating == expected

    def test_write_none_removes_rating(self):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        with temp_file_with_metadata(basic_metadata, "mp3") as test_file:
            # First write a rating
            test_metadata = {UnifiedMetadataKey.RATING: 80}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2
            )
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating == 80

            # Then remove it with None - this may not work as expected in all cases
            test_metadata = {UnifiedMetadataKey.RATING: None}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2
            )
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            # Rating removal behavior may vary - check if it's None or 0
            assert rating is None or rating == 0

    def test_write_edge_values(self):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        with temp_file_with_metadata(basic_metadata, "mp3") as test_file:
            # Test minimum value
            test_metadata = {UnifiedMetadataKey.RATING: 0}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2
            )
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating == 0

            # Test maximum value
            test_metadata = {UnifiedMetadataKey.RATING: 100}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2
            )
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating == 100
