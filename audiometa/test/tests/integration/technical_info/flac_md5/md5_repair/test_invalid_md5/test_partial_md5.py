from pathlib import Path

import pytest

from audiometa import FlacMd5State, fix_md5_checking, is_flac_md5_valid
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import corrupt_md5, ensure_flac_has_md5


@pytest.mark.integration
class TestPartialMd5:
    def test_fix_md5_checking_with_partial_corruption(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "partial")

            assert is_flac_md5_valid(test_file) == FlacMd5State.INVALID, "Partially corrupted MD5 should be INVALID"

            fixed_file_path = fix_md5_checking(test_file)
            assert is_flac_md5_valid(fixed_file_path) == FlacMd5State.VALID, "Fixed file should have valid MD5"

            Path(fixed_file_path).unlink()
