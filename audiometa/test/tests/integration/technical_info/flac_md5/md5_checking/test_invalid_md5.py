"""Test invalid MD5 validation."""

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import corrupt_md5, ensure_flac_has_md5


@pytest.mark.integration
class TestInvalidMd5:
    def test_is_flac_md5_valid_detects_random_md5_corruption(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "random")

            assert (
                is_flac_md5_valid(test_file) == FlacMd5State.INVALID
            ), "Random MD5 corruption should be detected as INVALID"

    def test_is_flac_md5_valid_detects_partial_md5_corruption(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "partial")

            assert (
                is_flac_md5_valid(test_file) == FlacMd5State.INVALID
            ), "Partially corrupted MD5 should be detected as INVALID"

    def test_is_flac_md5_valid_detects_flipped_md5(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "flip_all")

            assert is_flac_md5_valid(test_file) == FlacMd5State.INVALID, "Flipped MD5 should be detected as INVALID"
