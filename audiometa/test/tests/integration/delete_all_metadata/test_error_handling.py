import pytest

from audiometa import delete_all_metadata
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.integration
class TestDeleteAllMetadataErrorHandling:
    def test_delete_all_metadata_unsupported_file_type(self):
        # Create a file with unsupported extension
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            temp_audio_file_path.write_bytes(b"fake audio content")
            txt_file_path = temp_audio_file_path.with_suffix(".txt")
            txt_file_path.write_bytes(b"fake audio content")

            with pytest.raises(FileTypeNotSupportedError):
                delete_all_metadata(str(txt_file_path))

    def test_delete_all_metadata_nonexistent_file(self):
        nonexistent_file = "nonexistent_file.mp3"

        with pytest.raises(FileNotFoundError):
            delete_all_metadata(nonexistent_file)
