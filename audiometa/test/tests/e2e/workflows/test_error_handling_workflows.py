"""End-to-end tests for error handling and recovery workflows.

These tests verify that the system handles errors gracefully and recovers properly from various error conditions in
real-world scenarios.
"""

import pytest

from audiometa import delete_all_metadata, get_bitrate, get_duration_in_sec, get_unified_metadata, update_metadata
from audiometa.exceptions import InvalidMetadataFieldFormatError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.e2e
class TestErrorHandlingWorkflows:
    def test_error_recovery_workflow(self):
        # E2E test for error scenarios
        # Use external script to set initial metadata
        initial_metadata = {"title": "Original Title", "artist": "Original Artist"}
        with temp_file_with_metadata(initial_metadata, "mp3") as test_file_path:
            # Test invalid operations - try to update with rating without normalized_rating_max_value
            with pytest.raises(Exception):  # ConfigurationError
                update_metadata(test_file_path, {UnifiedMetadataKey.RATING: 75})  # Missing normalized_rating_max_value

            # Test recovery after errors
            test_metadata = {UnifiedMetadataKey.TITLE: "Recovery Test"}
            update_metadata(test_file_path, test_metadata)

            # Verify the file is still usable
            metadata = get_unified_metadata(test_file_path)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "Recovery Test"

    def test_error_handling_workflow(self):
        # Create a file with unsupported extension
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            temp_audio_file_path.write_bytes(b"fake audio content")
            test_file = temp_audio_file_path.with_suffix(".txt")
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
        initial_metadata = {"title": "Deletion Error Test", "artist": "Deletion Error Artist"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file_path:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file_path)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Deletion Error Test"

            # 2. Test deletion on file that doesn't exist
            non_existent_file = test_file_path.parent / "non_existent.mp3"
            with pytest.raises(Exception):  # FileNotFoundError
                delete_all_metadata(str(non_existent_file))

            # 3. Test deletion on directory instead of file
            with pytest.raises(Exception):  # IsADirectoryError or similar
                delete_all_metadata(str(test_file_path.parent))

            # 4. Verify original file is still usable after errors
            metadata_after_errors = get_unified_metadata(test_file_path)
            assert metadata_after_errors.get(UnifiedMetadataKey.TITLE) == "Deletion Error Test"

            # 5. Successfully delete metadata from original file
            delete_result = delete_all_metadata(test_file_path)
            assert delete_result is True

            # 6. Verify deletion worked
            deleted_metadata = get_unified_metadata(test_file_path)
            assert (
                deleted_metadata.get(UnifiedMetadataKey.TITLE) is None
                or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "Deletion Error Test"
            )

    def test_deletion_with_corrupted_metadata_workflow(self):
        # E2E test for deletion when metadata might be corrupted
        initial_metadata = {"title": "Corrupted Metadata Test", "artist": "Corrupted Artist"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file_path:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file_path)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Corrupted Metadata Test"

            # 2. Try to delete metadata - should work even if some metadata is corrupted
            delete_result = delete_all_metadata(test_file_path)
            assert delete_result is True

            # 3. Verify deletion worked
            deleted_metadata = get_unified_metadata(test_file_path)
            assert (
                deleted_metadata.get(UnifiedMetadataKey.TITLE) is None
                or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "Corrupted Metadata Test"
            )

            # 4. Verify file is still usable after deletion
            # Try to add new metadata
            new_metadata = {UnifiedMetadataKey.TITLE: "New Title After Deletion"}
            update_metadata(test_file_path, new_metadata)

            # 5. Verify new metadata was added successfully
            new_metadata_result = get_unified_metadata(test_file_path)
            assert new_metadata_result.get(UnifiedMetadataKey.TITLE) == "New Title After Deletion"

    def test_date_format_validation_workflow(self):
        initial_metadata = {"title": "Date Validation Test", "artist": "Date Test Artist"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file_path:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file_path)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Date Validation Test"

            # 2. Test invalid date formats - should raise InvalidMetadataFieldFormatError
            invalid_dates = [
                "2024/01/01",
                "2024-1-1",
                "not-a-date",
                "24",
            ]

            for invalid_date in invalid_dates:
                with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
                    update_metadata(test_file_path, {UnifiedMetadataKey.RELEASE_DATE: invalid_date})
                error = exc_info.value
                assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
                assert error.value == invalid_date

            # 3. Verify file is still usable after validation errors (validation happens before file write)
            metadata_after_errors = get_unified_metadata(test_file_path)
            assert metadata_after_errors.get(UnifiedMetadataKey.TITLE) == "Date Validation Test"

            # 4. Test valid date format - should succeed
            # Update with valid YYYY-MM-DD format
            update_metadata(test_file_path, {UnifiedMetadataKey.RELEASE_DATE: "2024-01-01"})
            updated_metadata = get_unified_metadata(test_file_path)
            assert updated_metadata.get(UnifiedMetadataKey.RELEASE_DATE) == "2024-01-01"
