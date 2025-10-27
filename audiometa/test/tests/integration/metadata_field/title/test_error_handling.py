import pytest
from pathlib import Path

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.integration
class TestTitleErrorHandling:

    def test_title_unsupported_file_type(self, temp_audio_file: Path):
        temp_audio_file.write_bytes(b"fake audio content")
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            get_unified_metadata_field(str(temp_audio_file), UnifiedMetadataKey.TITLE)
        
        with pytest.raises(FileTypeNotSupportedError):
            update_metadata(str(temp_audio_file), {UnifiedMetadataKey.TITLE: "Test Title"})

    def test_title_nonexistent_file(self):
        nonexistent_file = "nonexistent_file.mp3"
        
        with pytest.raises(FileNotFoundError):
            get_unified_metadata_field(nonexistent_file, UnifiedMetadataKey.TITLE)
        
        with pytest.raises(FileNotFoundError):
            update_metadata(nonexistent_file, {UnifiedMetadataKey.TITLE: "Test Title"})

    def test_title_empty_values(self, sample_mp3_file: Path, temp_audio_file: Path):
        # Test with empty title values
        temp_audio_file.write_bytes(sample_mp3_file.read_bytes())
        
        # Empty string should be handled gracefully
        update_metadata(temp_audio_file, {UnifiedMetadataKey.TITLE: ""})
        title = get_unified_metadata_field(temp_audio_file, UnifiedMetadataKey.TITLE)
        assert title == "" or title is None
        
        # None should be handled gracefully
        update_metadata(temp_audio_file, {UnifiedMetadataKey.TITLE: None})
        title = get_unified_metadata_field(temp_audio_file, UnifiedMetadataKey.TITLE)
        assert title is None or title == ""
