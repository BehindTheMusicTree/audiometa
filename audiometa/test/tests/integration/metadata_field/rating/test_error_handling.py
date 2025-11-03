import pytest
from pathlib import Path

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.exceptions import FileTypeNotSupportedError, InvalidMetadataFieldTypeError, ConfigurationError, InvalidRatingValueError


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

    def test_rating_without_max_value_validates_against_write_profile(self):
        with TempFileWithMetadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            # Valid value in BASE_255_NON_PROPORTIONAL profile (ID3v2 uses this)
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 128}, metadata_format=MetadataFormat.ID3V2)
            
            # Invalid value not in write profile - should raise error
            with pytest.raises(InvalidRatingValueError) as exc_info:
                update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 75}, metadata_format=MetadataFormat.ID3V2)
            assert "does not correspond to any value in the write profile" in str(exc_info.value)
            
            # Valid value in BASE_100_PROPORTIONAL profile (Vorbis uses this)
            with TempFileWithMetadata({"title": "Test Title", "artist": "Test Artist"}, "flac") as test_file_flac:
                update_metadata(test_file_flac.path, {UnifiedMetadataKey.RATING: 50}, metadata_format=MetadataFormat.VORBIS)
                
                # Invalid value for Vorbis profile
                with pytest.raises(InvalidRatingValueError) as exc_info:
                    update_metadata(test_file_flac.path, {UnifiedMetadataKey.RATING: 128}, metadata_format=MetadataFormat.VORBIS)
                assert "does not correspond to any value in the write profile" in str(exc_info.value)

    def test_rating_with_normalized_max_validates_tenth_ratio(self):
        with TempFileWithMetadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            # Valid tenth ratio of 100 (50 * 10 % 100 == 0)
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 50}, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            
            # Invalid - not a tenth ratio (37 * 10 % 100 == 70 != 0)
            with pytest.raises(InvalidRatingValueError) as exc_info:
                update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 37}, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2)
            assert "not a valid tenth ratio" in str(exc_info.value)

    def test_invalid_rating_value_error_non_numeric_string(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.RATING: "invalid"},
                    normalized_rating_max_value=100
                )
            assert "invalid type for metadata field 'rating'" in str(exc_info.value).lower()

    def test_invalid_rating_value_error_non_numeric_type(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.RATING: {"not": "valid"}},
                    normalized_rating_max_value=100
                )
            assert "invalid type for metadata field 'rating'" in str(exc_info.value).lower()
