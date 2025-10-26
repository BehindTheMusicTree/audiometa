

import pytest
from pathlib import Path

from audiometa import is_flac_md5_valid, fix_md5_checking
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.unit
class TestFlacMd5Functions:

    def test_is_flac_md5_valid_flac(self, sample_flac_file: Path):
        is_valid = is_flac_md5_valid(sample_flac_file)
        assert isinstance(is_valid, bool)

    def test_is_flac_md5_valid_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            is_flac_md5_valid(sample_mp3_file)

    def test_is_flac_md5_valid_with_audio_file_object(self, sample_flac_file: Path):
        from audiometa import AudioFile
        audio_file = AudioFile(sample_flac_file)
        is_valid = is_flac_md5_valid(audio_file)
        assert isinstance(is_valid, bool)

    def test_fix_md5_checking_flac(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            # Fix MD5 checking
            fixed_file_path = fix_md5_checking(test_file.path)
            assert isinstance(fixed_file_path, str)
            assert Path(fixed_file_path).exists()
            
            # Clean up
            Path(fixed_file_path).unlink()

    def test_fix_md5_checking_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            fix_md5_checking(sample_mp3_file)

    def test_fix_md5_checking_with_audio_file_object(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            from audiometa import AudioFile
            audio_file = AudioFile(test_file.path)
            
            # Fix MD5 checking
            fixed_file_path = fix_md5_checking(audio_file)
            assert isinstance(fixed_file_path, str)
            assert Path(fixed_file_path).exists()
            
            # Clean up
            Path(fixed_file_path).unlink()
