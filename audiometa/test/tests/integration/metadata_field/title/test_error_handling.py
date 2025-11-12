from pathlib import Path

import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestTitleErrorHandling:
    def test_title_unsupported_file_type(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            temp_file_path.write_bytes(b"fake audio content")
            temp_txt = temp_file_path.with_suffix(".txt")
            temp_txt.write_bytes(b"fake audio content")

            with pytest.raises(FileTypeNotSupportedError):
                get_unified_metadata_field(str(temp_txt), UnifiedMetadataKey.TITLE)

            with pytest.raises(FileTypeNotSupportedError):
                update_metadata(str(temp_txt), {UnifiedMetadataKey.TITLE: "Test Title"})

    def test_title_nonexistent_file(self):
        nonexistent_file = "nonexistent_file.mp3"

        with pytest.raises(FileNotFoundError):
            get_unified_metadata_field(nonexistent_file, UnifiedMetadataKey.TITLE)

        with pytest.raises(FileNotFoundError):
            update_metadata(nonexistent_file, {UnifiedMetadataKey.TITLE: "Test Title"})

    def test_title_empty_values(self, sample_mp3_file: Path):
        # Test with empty title values using temp file with sample content
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            temp_file_path.write_bytes(sample_mp3_file.read_bytes())

            # Empty string should be handled gracefully
            update_metadata(temp_file_path, {UnifiedMetadataKey.TITLE: ""})
            title = get_unified_metadata_field(temp_file_path, UnifiedMetadataKey.TITLE)
            assert title == "" or title is None

            # None should be handled gracefully
            update_metadata(temp_file_path, {UnifiedMetadataKey.TITLE: None})
            title = get_unified_metadata_field(temp_file_path, UnifiedMetadataKey.TITLE)
            assert title is None or title == ""
