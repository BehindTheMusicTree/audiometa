import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestComprehensiveRatingWriting:
    def test_write_read_with_different_max_values(self):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        with temp_file_with_metadata(basic_metadata, "mp3") as test_file:
            # Write with base 100
            test_metadata = {UnifiedMetadataKey.RATING: 50}  # 2.5 stars
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2
            )

            # Read back with base 100
            rating_100 = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100
            )
            assert rating_100 == 50

            # Read back with base 255 (should be normalized)
            rating_255 = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=255
            )
            assert rating_255 is not None
            assert isinstance(rating_255, int | float)
            assert rating_255 > 0

    def test_cross_metadata_format_rating_consistency(self):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        test_rating = 70

        # Test ID3v2 metadata format
        with temp_file_with_metadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: test_rating}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2
            )
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating is not None
            assert isinstance(rating, int | float)
            assert rating > 0

        # Test RIFF metadata format
        with temp_file_with_metadata(basic_metadata, "wav") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: test_rating}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.RIFF
            )
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating is not None
            assert isinstance(rating, int | float)
            assert rating > 0

        # Test Vorbis metadata format
        with temp_file_with_metadata(basic_metadata, "flac") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: test_rating}
            update_metadata(
                test_file, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.VORBIS
            )
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating is not None
            assert isinstance(rating, int | float)
            assert rating > 0

    def test_metadata_format_specific_rating_profiles(self):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        # Test ID3v2 with base 255 non-proportional values
        with temp_file_with_metadata(basic_metadata, "mp3") as test_file:
            test_values = [0, 1, 64, 128, 196, 255]
            for value in test_values:
                test_metadata = {UnifiedMetadataKey.RATING: value}
                update_metadata(
                    test_file, test_metadata, normalized_rating_max_value=255, metadata_format=MetadataFormat.ID3V2
                )
                rating = get_unified_metadata_field(
                    test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=255
                )
                assert rating is not None
                assert isinstance(rating, int | float)
                assert 0 <= rating <= 255

        # Test Vorbis with base 100 proportional values
        with temp_file_with_metadata(basic_metadata, "flac") as test_file:
            test_values = [0, 20, 40, 60, 80, 100]
            for value in test_values:
                test_metadata = {UnifiedMetadataKey.RATING: value}
                update_metadata(
                    test_file,
                    test_metadata,
                    normalized_rating_max_value=100,
                    metadata_format=MetadataFormat.VORBIS,
                )
                rating = get_unified_metadata_field(
                    test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100
                )
                assert rating is not None
                assert rating == value

    def test_rating_removal_consistency_across_formats(self):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        # Test rating removal behavior across all formats
        for format_type, file_ext in [
            (MetadataFormat.ID3V2, "mp3"),
            (MetadataFormat.RIFF, "wav"),
            (MetadataFormat.VORBIS, "flac"),
        ]:
            with temp_file_with_metadata(basic_metadata, file_ext) as test_file:
                # First write a rating
                test_metadata = {UnifiedMetadataKey.RATING: 80}
                update_metadata(test_file, test_metadata, normalized_rating_max_value=100, metadata_format=format_type)
                rating = get_unified_metadata_field(
                    test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100
                )
                assert rating == 80

                # Then remove it with None
                test_metadata = {UnifiedMetadataKey.RATING: None}
                update_metadata(test_file, test_metadata, normalized_rating_max_value=100, metadata_format=format_type)
                rating = get_unified_metadata_field(
                    test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100
                )
                # Rating removal behavior may vary - check if it's None or 0
                assert rating is None or rating == 0

    def test_write_float_rating_values_normalized_mode(self):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        # Test float values with max=10 (half-star ratings)
        with temp_file_with_metadata(basic_metadata, "mp3") as test_file:
            test_values = [1.5, 2.5, 3.5, 4.5, 7.5]
            for value in test_values:
                test_metadata = {UnifiedMetadataKey.RATING: value}
                update_metadata(
                    test_file, test_metadata, normalized_rating_max_value=10, metadata_format=MetadataFormat.ID3V2
                )
                rating = get_unified_metadata_field(
                    test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=10
                )
                assert rating is not None
                assert isinstance(rating, int | float)
                assert rating > 0

        # Test float values with max=100
        with temp_file_with_metadata(basic_metadata, "flac") as test_file:
            test_values = [1.5, 7.5, 15.0, 25.5, 50.0]
            for value in test_values:
                test_metadata = {UnifiedMetadataKey.RATING: value}
                update_metadata(
                    test_file,
                    test_metadata,
                    normalized_rating_max_value=100,
                    metadata_format=MetadataFormat.VORBIS,
                )
                rating = get_unified_metadata_field(
                    test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100
                )
                assert rating is not None
                assert isinstance(rating, int | float)
                assert rating >= 0

    @pytest.mark.parametrize("rating_value", [1.5, 75.7, 128.5])
    def test_write_float_rating_values_raw_mode(self, rating_value):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        # Test fractional float values in raw mode (no normalization) - should raise error
        from audiometa.exceptions import InvalidRatingValueError

        with temp_file_with_metadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: rating_value}
            with pytest.raises(InvalidRatingValueError) as exc_info:
                update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2)
            assert "In raw mode, float values must be whole numbers" in str(exc_info.value)

    @pytest.mark.parametrize("rating_value", [0.0, 128.0, 196.0, 255.0])
    def test_write_whole_number_float_rating_values_raw_mode(self, rating_value):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}

        # Test whole-number float values in raw mode (no normalization) - should be accepted and converted to int
        with temp_file_with_metadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: rating_value}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2)
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING)
            assert rating == int(rating_value)
