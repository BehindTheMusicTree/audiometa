"""Test unset MD5 validation."""

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
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

            # Unset MD5 (all zeros) should be detected as UNSET
            result = is_flac_md5_valid(test_file)
            assert result == FlacMd5State.UNSET, "Unset MD5 should be detected as UNSET"

    def test_is_flac_md5_valid_with_corrupted_to_unset_md5(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "zeros")

            # Unset MD5 (all zeros) should be detected as UNSET
            result = is_flac_md5_valid(test_file)
            assert result == FlacMd5State.UNSET, "Unset MD5 should be detected as UNSET"
