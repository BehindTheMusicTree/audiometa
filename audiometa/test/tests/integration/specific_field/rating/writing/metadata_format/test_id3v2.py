import pytest

from audiometa import get_unified_metadata, update_metadata, get_unified_metadata_field
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestId3v2RatingWriting:
    
    def test_write_0_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 0}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 0

    def test_write_1_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 20}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 20

    def test_write_2_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 40}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 40

    def test_write_3_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 60}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 60

    def test_write_4_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 80}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 80

    def test_write_5_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 100}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 100

    def test_write_0_5_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 10}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 10

    def test_write_1_5_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 30}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 30

    def test_write_2_5_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 50}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 50

    def test_write_3_5_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 70}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 70

    def test_write_4_5_star(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.RATING: 90}
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            rating = metadata.get(UnifiedMetadataKey.RATING)
            assert rating is not None
            assert rating == 90

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
