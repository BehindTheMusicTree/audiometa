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
            # Corrupt the MD5 checksum in the STREAMINFO block to ensure MD5 is invalid
            # The MD5 checksum is stored at bytes 18-33 in the STREAMINFO block (first metadata block)
            # STREAMINFO block starts after the 4-byte "fLaC" marker and 1-byte block header
            with test_file.open("r+b") as f:
                # Read the file to find STREAMINFO block
                data = f.read()
                # Find "fLaC" marker
                flac_marker_pos = data.find(b"fLaC")
                if flac_marker_pos == -1:
                    msg = "Could not find FLAC marker in test file"
                    raise RuntimeError(msg)
                # STREAMINFO block starts at flac_marker_pos + 4 (after "fLaC")
                # Block header is 1 byte, then STREAMINFO data starts
                # MD5 checksum is at offset 18-33 within STREAMINFO data
                md5_start = flac_marker_pos + 4 + 1 + 18
                if md5_start + 16 > len(data):
                    msg = "FLAC file too small to contain MD5 checksum"
                    raise RuntimeError(msg)
                # Corrupt the MD5 checksum by flipping all bits
                f.seek(md5_start)
                original_md5 = f.read(16)
                f.seek(md5_start)
                corrupted_md5 = bytes(b ^ 0xFF for b in original_md5)
                f.write(corrupted_md5)

            # Ensure we're testing with a FLAC file that has invalid MD5
            assert not is_flac_md5_valid(test_file), "Test file should have invalid MD5 for fix_md5_checking test"

            fixed_file_path = fix_md5_checking(test_file)
            assert is_flac_md5_valid(fixed_file_path), "Fixed file should have valid MD5"

            # Clean up
            Path(fixed_file_path).unlink()

    def test_fix_md5_checking_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            fix_md5_checking(sample_mp3_file)
