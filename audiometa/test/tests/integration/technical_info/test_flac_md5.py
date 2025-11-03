
import pytest
from pathlib import Path
import os

from audiometa import is_flac_md5_valid, fix_md5_checking
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestFlacMd5Functions:

    def test_is_flac_md5_valid_works_with_path_string(self, sample_flac_file: Path):
        is_valid = is_flac_md5_valid(str(sample_flac_file))
        assert isinstance(is_valid, bool)

    def test_is_flac_md5_valid_works_with_pathlib_path(self, sample_flac_file: Path):
        is_valid = is_flac_md5_valid(sample_flac_file)
        assert isinstance(is_valid, bool)

    def test_is_flac_md5_valid_works_with_audio_file_object(self, sample_flac_file: Path):
        from audiometa import AudioFile
        audio_file = AudioFile(sample_flac_file)
        is_valid = is_flac_md5_valid(audio_file)
        assert isinstance(is_valid, bool)

    def test_is_flac_md5_valid_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            is_flac_md5_valid(sample_mp3_file)

    def test_fix_md5_checking_flac(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            # Truncate the file to corrupt it and ensure MD5 is invalid
            with open(test_file.path, 'r+b') as f:
                f.truncate(os.path.getsize(test_file.path) - 100)  # Remove last 100 bytes
            
            # Ensure we're testing with a FLAC file that has invalid MD5
            assert not is_flac_md5_valid(test_file.path), "Test file should have invalid MD5 for fix_md5_checking test"
            
            fixed_file_path = fix_md5_checking(test_file.path)
            assert is_flac_md5_valid(fixed_file_path), "Fixed file should have valid MD5"
            
            # Clean up
            Path(fixed_file_path).unlink()

    def test_fix_md5_checking_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            fix_md5_checking(sample_mp3_file)

    def test_fix_md5_checking_with_audio_file_object(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            # Truncate the file to corrupt it and ensure MD5 is invalid
            with open(test_file.path, 'r+b') as f:
                f.truncate(os.path.getsize(test_file.path) - 100)  # Remove last 100 bytes
            
            from audiometa import AudioFile
            audio_file = AudioFile(test_file.path)
            
            assert not audio_file.is_flac_file_md5_valid()
            
            # Fix MD5 checking
            fixed_file_path = fix_md5_checking(audio_file)
            assert isinstance(fixed_file_path, str)
            assert Path(fixed_file_path).exists()
            
            # Clean up
            Path(fixed_file_path).unlink()

