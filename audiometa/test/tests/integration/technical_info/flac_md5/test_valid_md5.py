from pathlib import Path

import pytest

from audiometa import is_flac_md5_valid
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.integration
class TestValidFlacMd5:
    def test_is_flac_md5_valid_works_with_path_string(self, sample_flac_file: Path):
        is_valid = is_flac_md5_valid(str(sample_flac_file))
        assert isinstance(is_valid, bool)

    def test_is_flac_md5_valid_works_with_pathlib_path(self, sample_flac_file: Path):
        is_valid = is_flac_md5_valid(sample_flac_file)
        assert isinstance(is_valid, bool)

    def test_is_flac_md5_valid_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            is_flac_md5_valid(sample_mp3_file)
