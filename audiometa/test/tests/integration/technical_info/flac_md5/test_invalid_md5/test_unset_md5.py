from pathlib import Path

import pytest

from audiometa import fix_md5_checking, is_flac_md5_valid
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import (
    corrupt_md5,
    create_flac_without_md5,
    ensure_flac_has_md5,
)


@pytest.mark.integration
class TestUnsetMd5:
    def test_is_flac_md5_valid_with_naturally_unset_md5(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            # Create FLAC file without MD5 (naturally unset, not corrupted)
            create_flac_without_md5(test_file)

            # Unset MD5 (all zeros) should be consistently detected as invalid
            result = is_flac_md5_valid(test_file)
            assert result is False, "Unset MD5 should be detected as invalid"

    def test_is_flac_md5_valid_with_corrupted_to_unset_md5(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "zeros")

            # Unset MD5 (all zeros) should be consistently detected as invalid
            result = is_flac_md5_valid(test_file)
            assert result is False, "Unset MD5 should be detected as invalid"

    def test_fix_md5_checking_with_naturally_unset_md5(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            # Create FLAC file without MD5 (naturally unset, not corrupted)
            create_flac_without_md5(test_file)

            assert not is_flac_md5_valid(test_file), "Unset MD5 should be detected as invalid"

            fixed_file_path = fix_md5_checking(test_file)
            assert is_flac_md5_valid(fixed_file_path), "Fixed file should have valid MD5"

            Path(fixed_file_path).unlink()

    def test_fix_md5_checking_with_corrupted_to_unset_md5(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "zeros")

            assert not is_flac_md5_valid(test_file), "Unset MD5 should be detected as invalid"

            fixed_file_path = fix_md5_checking(test_file)
            assert is_flac_md5_valid(fixed_file_path), "Fixed file should have valid MD5"

            Path(fixed_file_path).unlink()
