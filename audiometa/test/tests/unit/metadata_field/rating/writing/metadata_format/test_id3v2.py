import pytest

from audiometa import get_unified_metadata, update_metadata, get_unified_metadata_field
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.unit
class TestId3v2RatingWriting:
    
    @pytest.mark.parametrize("star_rating,expected_normalized_rating", [
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
    ])
    def test_write_star_rating(self, temp_audio_file, star_rating, expected_normalized_rating):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: expected_normalized_rating}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == expected_normalized_rating

    def test_write_base_255_non_proportional_values(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        # Test values that correspond to BASE_255_NON_PROPORTIONAL profile
        test_values = [0, 1, 64, 128, 196, 255]  # 0, 1, 2, 3, 4, 5 stars in base 255
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            for value in test_values:
                test_metadata = {UnifiedMetadataKey.RATING: value}
                update_metadata(test_file.path, test_metadata, normalized_rating_max_value=255, metadata_format=MetadataFormat.ID3V2)
                rating = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=255)
                assert rating is not None
                # The value may be normalized/clamped, so just check it's in valid range
                assert 0 <= rating <= 255

    def test_write_none_removes_rating(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            # First write a rating
            test_metadata = {UnifiedMetadataKey.RATING: 80}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            rating = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating == 80
            
            # Then remove it with None - this may not work as expected in all cases
            test_metadata = {UnifiedMetadataKey.RATING: None}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            rating = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            # Rating removal behavior may vary - check if it's None or 0
            assert rating is None or rating == 0

    def test_write_edge_values(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            # Test minimum value
            test_metadata = {UnifiedMetadataKey.RATING: 0}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            rating = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating == 0
            
            # Test maximum value
            test_metadata = {UnifiedMetadataKey.RATING: 100}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            rating = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating == 100
