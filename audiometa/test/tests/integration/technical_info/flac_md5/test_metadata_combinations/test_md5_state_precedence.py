"""Test that state detection follows correct precedence rules for MD5 validation."""

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import (
    corrupt_md5,
    create_flac_without_md5,
    ensure_flac_has_md5,
)


@pytest.mark.integration
class TestMd5StatePrecedence:
    """Test that state detection follows correct precedence rules."""

    def test_unset_takes_precedence_over_uncheckable(self):
        """Test that UNSET state takes precedence over UNCHECKABLE_DUE_TO_ID3."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            create_flac_without_md5(test_file)
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNSET
            ), "UNSET should take precedence over UNCHECKABLE_DUE_TO_ID3 when MD5 is unset"

    def test_uncheckable_takes_precedence_over_invalid_when_id3v1_present(self):
        """Test that UNCHECKABLE_DUE_TO_ID3 takes precedence over INVALID when ID3v1 is present."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "UNCHECKABLE_DUE_TO_ID3 should take precedence over INVALID when ID3v1 is present"
