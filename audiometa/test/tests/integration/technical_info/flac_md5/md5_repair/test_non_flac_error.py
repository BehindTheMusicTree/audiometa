from pathlib import Path

import pytest

from audiometa import fix_md5_checking
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.integration
class TestNonFlacError:
    def test_fix_md5_checking_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            fix_md5_checking(sample_mp3_file)
