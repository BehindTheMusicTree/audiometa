from pathlib import Path

import pytest

from audiometa import fix_md5_checking, is_flac_md5_valid
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import corrupt_md5, ensure_flac_has_md5


@pytest.mark.integration
class TestFlippedMd5:
    def test_is_flac_md5_valid_detects_flipped_md5(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "flip_all")

            assert not is_flac_md5_valid(test_file), "Flipped MD5 should be detected as invalid"

    def test_fix_md5_checking_flac(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "flip_all")

            assert not is_flac_md5_valid(test_file), "Test file should have invalid MD5 for fix_md5_checking test"

            fixed_file_path = fix_md5_checking(test_file)
            assert is_flac_md5_valid(fixed_file_path), "Fixed file should have valid MD5"

            Path(fixed_file_path).unlink()
