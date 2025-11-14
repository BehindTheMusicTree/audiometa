"""End-to-end tests for error handling and recovery workflows.

These tests verify that the system handles errors gracefully and recovers properly from various error conditions in
real-world scenarios.
"""

import pytest

from audiometa import delete_all_metadata, get_bitrate, get_duration_in_sec, get_unified_metadata, update_metadata
from audiometa.exceptions import InvalidMetadataFieldFormatError, InvalidRatingValueError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.e2e
class TestErrorHandlingWorkflows:
    def test_error_recovery_workflow(self):
        # E2E test for error scenarios and recovery
        initial_metadata = {"title": "Original Title", "artist": "Original Artist"}
        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Original Title"

            # 2. Test invalid rating operation - should raise InvalidRatingValueError
            # Using normalized mode with invalid value (110 is over the max value and results in invalid star rating
            # index > 10)
            with pytest.raises(InvalidRatingValueError) as exc_info:
                update_metadata(test_file, {UnifiedMetadataKey.RATING: 110}, normalized_rating_max_value=100)
            assert "out of range" in str(exc_info.value) or "invalid star rating index" in str(exc_info.value)

            # 3. Test recovery after error - verify the file is still usable
            # The file should still have its original metadata intact
            metadata_after_error = get_unified_metadata(test_file)
            assert metadata_after_error.get(UnifiedMetadataKey.TITLE) == "Original Title"

            # 4. Test successful operation after error - should work normally
            recovery_metadata = {UnifiedMetadataKey.TITLE: "Recovery Test"}
            update_metadata(test_file, recovery_metadata)

            # 5. Verify recovery worked - file is fully functional
            final_metadata = get_unified_metadata(test_file)
            assert final_metadata.get(UnifiedMetadataKey.TITLE) == "Recovery Test"

    def test_error_handling_workflow(self):
        # Create a file with unsupported extension
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            temp_audio_file_path.write_bytes(b"fake audio content")
            test_file = temp_audio_file_path.with_suffix(".txt")
            test_file.write_bytes(b"fake audio content")

            # All operations should raise FileTypeNotSupportedError
            from audiometa.exceptions import FileTypeNotSupportedError

            with pytest.raises(FileTypeNotSupportedError):
                get_unified_metadata(str(test_file))

            with pytest.raises(FileTypeNotSupportedError):
                update_metadata(str(test_file), {UnifiedMetadataKey.TITLE: "Test"})

            with pytest.raises(FileTypeNotSupportedError):
                delete_all_metadata(str(test_file))

            with pytest.raises(FileTypeNotSupportedError):
                get_bitrate(str(test_file))

            with pytest.raises(FileTypeNotSupportedError):
                get_duration_in_sec(str(test_file))

    def test_deletion_error_recovery_workflow(self):
        # E2E test for deletion error scenarios and recovery
        initial_metadata = {"title": "Deletion Error Test", "artist": "Deletion Error Artist"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Deletion Error Test"

            # 2. Test deletion on file that doesn't exist
            non_existent_file = test_file.parent / "non_existent.mp3"
            with pytest.raises(FileNotFoundError):
                delete_all_metadata(str(non_existent_file))

            # 3. Test deletion on directory instead of file
            from audiometa.exceptions import FileTypeNotSupportedError

            with pytest.raises(FileTypeNotSupportedError):
                delete_all_metadata(str(test_file.parent))

            # 4. Verify original file is still usable after errors
            metadata_after_errors = get_unified_metadata(test_file)
            assert metadata_after_errors.get(UnifiedMetadataKey.TITLE) == "Deletion Error Test"

            # 5. Successfully delete metadata from original file
            delete_result = delete_all_metadata(test_file)
            assert delete_result is True

            # 6. Verify deletion worked
            deleted_metadata = get_unified_metadata(test_file)
            assert (
                deleted_metadata.get(UnifiedMetadataKey.TITLE) is None
                or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "Deletion Error Test"
            )

    def test_deletion_with_corrupted_metadata_workflow(self):
        # E2E test for deletion when metadata might be corrupted
        initial_metadata = {"title": "Corrupted Metadata Test", "artist": "Corrupted Artist"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Corrupted Metadata Test"

            # 2. Try to delete metadata - should work even if some metadata is corrupted
            delete_result = delete_all_metadata(test_file)
            assert delete_result is True

            # 3. Verify deletion worked
            deleted_metadata = get_unified_metadata(test_file)
            assert (
                deleted_metadata.get(UnifiedMetadataKey.TITLE) is None
                or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "Corrupted Metadata Test"
            )

            # 4. Verify file is still usable after deletion
            # Try to add new metadata
            new_metadata = {UnifiedMetadataKey.TITLE: "New Title After Deletion"}
            update_metadata(test_file, new_metadata)

            # 5. Verify new metadata was added successfully
            new_metadata_result = get_unified_metadata(test_file)
            assert new_metadata_result.get(UnifiedMetadataKey.TITLE) == "New Title After Deletion"

    def test_date_format_validation_workflow(self):
        initial_metadata = {"title": "Date Validation Test", "artist": "Date Test Artist"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file)
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
                    update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: invalid_date})
                error = exc_info.value
                assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
                assert error.value == invalid_date

            # 3. Verify file is still usable after validation errors (validation happens before file write)
            metadata_after_errors = get_unified_metadata(test_file)
            assert metadata_after_errors.get(UnifiedMetadataKey.TITLE) == "Date Validation Test"

            # 4. Test valid date format - should succeed
            # Update with valid YYYY-MM-DD format
            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: "2024-01-01"})
            updated_metadata = get_unified_metadata(test_file)
            assert updated_metadata.get(UnifiedMetadataKey.RELEASE_DATE) == "2024-01-01"
