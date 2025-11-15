from pathlib import Path

import pytest

from audiometa import fix_md5_checking, is_flac_md5_valid
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.integration
class TestFlacMd5Functions:
    def test_is_flac_md5_valid_works_with_path_string(self, sample_flac_file: Path):
        is_valid = is_flac_md5_valid(str(sample_flac_file))
        assert isinstance(is_valid, bool)

    def test_is_flac_md5_valid_works_with_pathlib_path(self, sample_flac_file: Path):
        is_valid = is_flac_md5_valid(sample_flac_file)
        assert isinstance(is_valid, bool)

    def test_is_flac_md5_valid_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            is_flac_md5_valid(sample_mp3_file)

    def test_fix_md5_checking_flac(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            # Corrupt audio data in the middle of the file to ensure MD5 is invalid
            # This is more reliable than truncation, which may not invalidate MD5 on all platforms
            file_size = test_file.stat().st_size
            with test_file.open("r+b") as f:
                # Corrupt bytes in the middle of the file (avoid header and end)
                # This will definitely invalidate the MD5 checksum
                corrupt_position = max(1000, file_size // 2)  # Middle of file, but at least 1000 bytes in
                f.seek(corrupt_position)
                original_bytes = f.read(100)
                f.seek(corrupt_position)
                # Flip all bits to corrupt the data
                corrupted_bytes = bytes(b ^ 0xFF for b in original_bytes)
                f.write(corrupted_bytes)

            # Ensure we're testing with a FLAC file that has invalid MD5
            assert not is_flac_md5_valid(test_file), "Test file should have invalid MD5 for fix_md5_checking test"

            fixed_file_path = fix_md5_checking(test_file)
            assert is_flac_md5_valid(fixed_file_path), "Fixed file should have valid MD5"

            # Clean up
            Path(fixed_file_path).unlink()

    def test_fix_md5_checking_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            fix_md5_checking(sample_mp3_file)
