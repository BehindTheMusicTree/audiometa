from pathlib import Path

import pytest

from audiometa import get_unified_metadata, get_unified_metadata_field
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestReadingErrorHandling:
    def test_unsupported_file_type_raises_error(self):
        # Create a file with unsupported extension
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            temp_audio_file_path.write_bytes(b"fake audio content")
            txt_file_path = temp_audio_file_path.with_suffix(".txt")
            txt_file_path.write_bytes(b"fake audio content")

            with pytest.raises(FileTypeNotSupportedError):
                get_unified_metadata(str(txt_file_path))

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
