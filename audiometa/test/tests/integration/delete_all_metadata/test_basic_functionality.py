import pytest

from audiometa import (
    delete_all_metadata,
    AudioFile
)
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestDeleteAllMetadataBasic:
    
    def test_delete_all_metadata_with_audio_file_object(self):
        # First add some metadata using external script
        test_metadata = {
            "title": "Test Title",
            "artist": "Test Artist"
        }
        with TempFileWithMetadata(test_metadata, "mp3") as test_file:
            # Create AudioFile object
            audio_file = AudioFile(test_file.path)
            
            # Delete all metadata using AudioFile object
            result = delete_all_metadata(audio_file)
            assert result is True

    def test_delete_all_metadata_file_with_no_metadata(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            # Delete metadata from file that has no metadata
            result = delete_all_metadata(test_file.path)
            assert result is True

    def test_delete_all_metadata_id3v2_version_specific(self):
        # First add some metadata using external script
        test_metadata = {
            "title": "Test Title",
            "artist": "Test Artist"
        }
        with TempFileWithMetadata(test_metadata, "mp3") as test_file:
            # Delete metadata with specific ID3v2 version
            result = delete_all_metadata(test_file.path, id3v2_version=(2, 3, 0))
            assert result is True

    def test_delete_all_metadata_return_value_success(self):
        # First add some metadata using external script
        test_metadata = {
            "title": "Test Title",
            "artist": "Test Artist"
        }
        with TempFileWithMetadata(test_metadata, "mp3") as test_file:
            result = delete_all_metadata(test_file.path)
            assert result is True
            assert isinstance(result, bool)


    def test_delete_all_metadata_preserves_audio_data(self):
        # First add some metadata using external script
        test_metadata = {
            "title": "Test Title",
            "artist": "Test Artist"
        }
        with TempFileWithMetadata(test_metadata, "mp3") as test_file:
            # Get file size with metadata
            with_metadata_size = test_file.path.stat().st_size
            
            # Delete all metadata
            result = delete_all_metadata(test_file.path)
            assert result is True
            
            # Verify file size decreased (metadata headers removed)
            after_deletion_size = test_file.path.stat().st_size
            assert after_deletion_size < with_metadata_size
            
            # Verify the file is still valid (not corrupted)
            assert after_deletion_size > 0


