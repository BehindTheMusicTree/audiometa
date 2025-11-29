"""Error handling tests for get_full_metadata function."""

import tempfile
from pathlib import Path

import pytest

from audiometa import get_full_metadata
from audiometa.exceptions import FileCorruptedError, FileTypeNotSupportedError


@pytest.mark.integration
class TestGetFullMetadataErrorHandling:
    def test_get_full_metadata_corrupted_file(self):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name
            # Write some garbage data
            temp_file.write(b"This is not a valid audio file")

        try:
            with pytest.raises(FileCorruptedError):
                get_full_metadata(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_get_full_metadata_error_recovery(self):
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            get_full_metadata("non_existent_file.mp3")

        # Test with unsupported file type (create the file first)
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(b"This is not an audio file")

        try:
            with pytest.raises(FileTypeNotSupportedError):
                get_full_metadata(temp_path)
        finally:
            Path(temp_path).unlink()
