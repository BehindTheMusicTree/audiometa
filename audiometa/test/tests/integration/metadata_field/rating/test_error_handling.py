import pytest
from pathlib import Path

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.exceptions import FileTypeNotSupportedError, InvalidMetadataFieldTypeError


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
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 25.5}, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)

    def test_rating_invalid_string_value(self):
        with TempFileWithMetadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            with pytest.raises(InvalidMetadataFieldTypeError, match="Invalid type for metadata field 'rating': expected int, got str"):
                update_metadata(test_file.path, {UnifiedMetadataKey.RATING: "invalid"}, normalized_rating_max_value=100)

    def test_rating_negative_value_clamping(self):
        with TempFileWithMetadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: -1}, normalized_rating_max_value=100)
            metadata = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert metadata == 0  # Should be clamped to 0

    def test_rating_over_max_value_clamping(self):
        with TempFileWithMetadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 101}, normalized_rating_max_value=100)
            metadata = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert metadata == 100  # Should be clamped to 100

    def test_rating_none_value(self):
        with TempFileWithMetadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: None}, normalized_rating_max_value=100)
            metadata = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert metadata is None
