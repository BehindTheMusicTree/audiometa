import pytest
from pathlib import Path

from audiometa import (
    get_unified_metadata,
    get_unified_metadata_field
)
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.integration
class TestReadingErrorHandling:

    def test_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        # Create a file with unsupported extension
        temp_audio_file.write_bytes(b"fake audio content")
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            get_unified_metadata(str(temp_audio_file))

    def test_nonexistent_file_raises_error(self):
        nonexistent_file = "nonexistent_file.mp3"
        
        with pytest.raises(FileNotFoundError):
            get_unified_metadata(nonexistent_file)
                
        with pytest.raises(FileNotFoundError):
            get_unified_metadata_field(nonexistent_file, UnifiedMetadataKey.TITLE)

    def test_metadata_key_not_found_returns_none(self, sample_mp3_file: Path):
        # This should not raise an error, but return None when the field is not found
        # Using a valid UnifiedMetadataKey that might not be present in the file
        result = get_unified_metadata_field(sample_mp3_file, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS)
        assert result is None