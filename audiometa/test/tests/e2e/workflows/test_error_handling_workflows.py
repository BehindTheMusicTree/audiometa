"""
End-to-end tests for error handling and recovery workflows.

These tests verify that the system handles errors gracefully and recovers
properly from various error conditions in real-world scenarios.
"""
import pytest
from pathlib import Path

from audiometa import (
    get_unified_metadata,
    update_metadata,
    delete_all_metadata,
    get_bitrate,
    get_duration_in_sec
)
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.e2e
class TestErrorHandlingWorkflows:

    def test_error_recovery_workflow(self):
        # E2E test for error scenarios
        # Use external script to set initial metadata
        initial_metadata = {
            "title": "Original Title",
            "artist": "Original Artist"
        }
        with TempFileWithMetadata(initial_metadata, "mp3") as test_file:
            # Test invalid operations - try to update with rating without normalized_rating_max_value
            with pytest.raises(Exception):  # ConfigurationError
                update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 75})  # Missing normalized_rating_max_value
        
            # Test recovery after errors
            test_metadata = {UnifiedMetadataKey.TITLE: "Recovery Test"}
            update_metadata(test_file.path, test_metadata)
        
            # Verify the file is still usable
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "Recovery Test"

    def test_error_handling_workflow(self, temp_audio_file: Path):
        # Create a file with unsupported extension
        temp_audio_file.write_bytes(b"fake audio content")
        test_file = temp_audio_file.with_suffix(".txt")
        test_file.write_bytes(b"fake audio content")
        
        # All operations should raise FileTypeNotSupportedError
        with pytest.raises(Exception):  # FileTypeNotSupportedError
            get_unified_metadata(str(test_file))
        
        with pytest.raises(Exception):  # FileTypeNotSupportedError
            update_metadata(str(test_file), {UnifiedMetadataKey.TITLE: "Test"})
        
        with pytest.raises(Exception):  # FileTypeNotSupportedError
            delete_all_metadata(str(test_file))
        
        with pytest.raises(Exception):  # FileTypeNotSupportedError
            get_bitrate(str(test_file))
        
        with pytest.raises(Exception):  # FileTypeNotSupportedError
            get_duration_in_sec(str(test_file))

    def test_deletion_error_recovery_workflow(self):
        # E2E test for deletion error scenarios and recovery
        initial_metadata = {
            "title": "Deletion Error Test",
            "artist": "Deletion Error Artist"
        }
        
        with TempFileWithMetadata(initial_metadata, "mp3") as test_file:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Deletion Error Test"
            
            # 2. Test deletion on file that doesn't exist
            non_existent_file = test_file.path.parent / "non_existent.mp3"
            with pytest.raises(Exception):  # FileNotFoundError
                delete_all_metadata(str(non_existent_file))
            
            # 3. Test deletion on directory instead of file
            with pytest.raises(Exception):  # IsADirectoryError or similar
                delete_all_metadata(str(test_file.parent))
            
            # 4. Verify original file is still usable after errors
            metadata_after_errors = get_unified_metadata(test_file)
            assert metadata_after_errors.get(UnifiedMetadataKey.TITLE) == "Deletion Error Test"
            
            # 5. Successfully delete metadata from original file
            delete_result = delete_all_metadata(test_file)
            assert delete_result is True
            
            # 6. Verify deletion worked
            deleted_metadata = get_unified_metadata(test_file)
            assert deleted_metadata.get(UnifiedMetadataKey.TITLE) is None or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "Deletion Error Test"

    def test_deletion_with_corrupted_metadata_workflow(self):
        # E2E test for deletion when metadata might be corrupted
        initial_metadata = {
            "title": "Corrupted Metadata Test",
            "artist": "Corrupted Artist"
        }
        
        with TempFileWithMetadata(initial_metadata, "mp3") as test_file:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Corrupted Metadata Test"
            
            # 2. Try to delete metadata - should work even if some metadata is corrupted
            delete_result = delete_all_metadata(test_file)
            assert delete_result is True
            
            # 3. Verify deletion worked
            deleted_metadata = get_unified_metadata(test_file)
            assert deleted_metadata.get(UnifiedMetadataKey.TITLE) is None or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "Corrupted Metadata Test"
            
            # 4. Verify file is still usable after deletion
            # Try to add new metadata
            new_metadata = {
                UnifiedMetadataKey.TITLE: "New Title After Deletion"
            }
            update_metadata(test_file.path, new_metadata)
            
            # 5. Verify new metadata was added successfully
            new_metadata_result = get_unified_metadata(test_file)
            assert new_metadata_result.get(UnifiedMetadataKey.TITLE) == "New Title After Deletion"
