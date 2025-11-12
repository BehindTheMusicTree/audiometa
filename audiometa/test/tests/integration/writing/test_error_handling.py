import pytest

from audiometa import delete_all_metadata, update_metadata
from audiometa.exceptions import FileTypeNotSupportedError, MetadataWritingConflictParametersError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.metadata_writing_strategy import MetadataWritingStrategy
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestWritingErrorHandling:
    def test_unsupported_file_type_raises_error(self):
        # Create a file with unsupported extension using temp_file_with_metadata
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            temp_file_path.write_bytes(b"fake audio content")
            temp_txt = temp_file_path.with_suffix(".txt")
            temp_txt.write_bytes(b"fake audio content")

            with pytest.raises(FileTypeNotSupportedError):
                update_metadata(str(temp_txt), {UnifiedMetadataKey.TITLE: "Test"})

            with pytest.raises(FileTypeNotSupportedError):
                delete_all_metadata(str(temp_txt))

    def test_nonexistent_file_raises_error(self):
        nonexistent_file = "nonexistent_file.mp3"

        with pytest.raises(FileNotFoundError):
            update_metadata(nonexistent_file, {UnifiedMetadataKey.TITLE: "Test"})

        # Note: delete_all_metadata error handling tests have been moved to test_delete_all_metadata.py

    def test_metadata_writing_conflict_parameters_error_both_strategy_and_format(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            with pytest.raises(MetadataWritingConflictParametersError) as exc_info:
                update_metadata(
                    test_file,
                    {UnifiedMetadataKey.TITLE: "Test"},
                    metadata_strategy=MetadataWritingStrategy.SYNC,
                    metadata_format=MetadataFormat.ID3V2,
                )
            assert "metadata_strategy" in str(exc_info.value).lower()
            assert "metadata_format" in str(exc_info.value).lower()
