import pytest
from pathlib import Path

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.exceptions import FileTypeNotSupportedError, InvalidRatingValueError


@pytest.mark.integration
class TestRatingErrorHandling:

    def test_rating_unsupported_file_type(self, temp_audio_file: Path):
        temp_audio_file.write_bytes(b"fake audio content")
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            get_unified_metadata_field(str(temp_audio_file), UnifiedMetadataKey.RATING)
        
        with pytest.raises(FileTypeNotSupportedError):
            update_metadata(str(temp_audio_file), {UnifiedMetadataKey.RATING: 85})

    def test_rating_nonexistent_file(self):
        nonexistent_file = "nonexistent_file.mp3"
        
        with pytest.raises(FileNotFoundError):
            get_unified_metadata_field(nonexistent_file, UnifiedMetadataKey.RATING)
        
        with pytest.raises(FileNotFoundError):
            update_metadata(nonexistent_file, {UnifiedMetadataKey.RATING: 85})
            

    def test_write_fractional_values(self, temp_audio_file):
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        
        with TempFileWithMetadata(basic_metadata, "mp3") as test_file:
            with pytest.raises(InvalidRatingValueError):
                update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 25.5}, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)

    def test_rating_invalid_values(self, sample_mp3_file: Path, temp_audio_file: Path):
        # Test with invalid rating values
        temp_audio_file.write_bytes(sample_mp3_file.read_bytes())
        
        # Test invalid string value - should raise InvalidRatingValueError
        with pytest.raises(InvalidRatingValueError, match="Invalid rating value: invalid. Expected a numeric value."):
            update_metadata(temp_audio_file, {UnifiedMetadataKey.RATING: "invalid"}, normalized_rating_max_value=100)
        
        # Test out-of-range numeric values - should be clamped to valid range
        # -1 should be clamped to 0 (0 stars)
        temp_audio_file.write_bytes(sample_mp3_file.read_bytes())  # Fresh file
        update_metadata(temp_audio_file, {UnifiedMetadataKey.RATING: -1}, normalized_rating_max_value=100)
        metadata = get_unified_metadata_field(temp_audio_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
        assert metadata == 0  # Should be clamped to 0
        
        # 101 should be clamped to 100 (5 stars)
        temp_audio_file.write_bytes(sample_mp3_file.read_bytes())  # Fresh file
        update_metadata(temp_audio_file, {UnifiedMetadataKey.RATING: 101}, normalized_rating_max_value=100)
        metadata = get_unified_metadata_field(temp_audio_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
        assert metadata == 100  # Should be clamped to 100
        
        # Test None value (should be handled gracefully by removing the rating)
        temp_audio_file.write_bytes(sample_mp3_file.read_bytes())  # Fresh file
        update_metadata(temp_audio_file, {UnifiedMetadataKey.RATING: None}, normalized_rating_max_value=100)
        metadata = get_unified_metadata_field(temp_audio_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
        assert metadata is None
