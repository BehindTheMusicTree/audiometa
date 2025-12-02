"""Test that ID3v2 tags alone do NOT cause validation failures."""

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import corrupt_md5, ensure_flac_has_md5


@pytest.mark.integration
class TestMd5ValidationWithId3v2Only:
    """Test that ID3v2 tags alone do NOT cause validation failures.

    These tests verify that ID3v2 tags (without ID3v1) do not interfere with validation
    and return appropriate states (VALID or INVALID) based on actual MD5 state.
    """

    def test_id3v2_alone_with_valid_md5_returns_valid(self):
        """Test that ID3v2 tags alone with valid MD5 return VALID (not UNCHECKABLE)."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.VALID
            ), "ID3v2 tags alone with valid MD5 should return VALID, not UNCHECKABLE_DUE_TO_ID3"

    def test_id3v2_alone_with_invalid_md5_returns_invalid(self):
        """Test that ID3v2 tags alone with invalid MD5 return INVALID (not UNCHECKABLE).

        This confirms that ID3v2 tags do NOT cause validation failures - even with
        corrupted MD5, we get INVALID (actual corruption) rather than UNCHECKABLE_DUE_TO_ID3.
        """
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.INVALID
            ), "ID3v2 alone with invalid MD5 returns INVALID, not UNCHECKABLE. Proves ID3v2 doesn't cause failures."
