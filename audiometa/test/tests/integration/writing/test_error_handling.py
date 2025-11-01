import pytest
from pathlib import Path

from audiometa import (
    update_metadata,
    delete_all_metadata
)
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.MetadataWritingStrategy import MetadataWritingStrategy
from audiometa.exceptions import FileTypeNotSupportedError, MetadataWritingConflictParametersError
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestWritingErrorHandling:

    def test_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        # Create a file with unsupported extension
        temp_audio_file.write_bytes(b"fake audio content")
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            update_metadata(str(temp_audio_file), {UnifiedMetadataKey.TITLE: "Test"})
        
        with pytest.raises(FileTypeNotSupportedError):
            delete_all_metadata(str(temp_audio_file))

    def test_nonexistent_file_raises_error(self):
        nonexistent_file = "nonexistent_file.mp3"
        
        with pytest.raises(FileNotFoundError):
            update_metadata(nonexistent_file, {UnifiedMetadataKey.TITLE: "Test"})
        
        # Note: delete_all_metadata error handling tests have been moved to test_delete_all_metadata.py

    def test_metadata_writing_conflict_parameters_error_both_strategy_and_format(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataWritingConflictParametersError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.TITLE: "Test"},
                    metadata_strategy=MetadataWritingStrategy.SYNC,
                    metadata_format=MetadataFormat.ID3V2
                )
            assert "metadata_strategy" in str(exc_info.value).lower()
            assert "metadata_format" in str(exc_info.value).lower()
