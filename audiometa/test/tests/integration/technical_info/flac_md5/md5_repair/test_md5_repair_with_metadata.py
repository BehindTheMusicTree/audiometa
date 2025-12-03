"""Test MD5 repair with metadata combinations."""

import warnings
from pathlib import Path

import pytest

from audiometa import FlacMd5State, fix_md5_checking, is_flac_md5_valid
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v1.id3v1_header_verifier import ID3v1HeaderVerifier
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import ensure_flac_has_md5


@pytest.mark.integration
class TestMd5RepairWithMetadata:
    """Test MD5 repair with metadata combinations."""

    def test_fix_md5_checking_with_id3v1_metadata(self):
        """Test that fix_md5_checking repairs MD5 and removes ID3v1 tags."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v1MetadataSetter.set_artist(test_file, "ID3v1 Artist")

            # Verify initial state: UNCHECKABLE_DUE_TO_ID3V1
            initial_state = is_flac_md5_valid(test_file)
            assert (
                initial_state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "File with ID3v1 should be UNCHECKABLE_DUE_TO_ID3V1"
            assert ID3v1HeaderVerifier.has_id3v1_header(test_file), "File should have ID3v1 header initially"

            # Repair the MD5
            fixed_file_path = fix_md5_checking(test_file)

            # Verify repair results: VALID MD5 and ID3v1 tags removed
            final_state = is_flac_md5_valid(fixed_file_path)
            assert final_state == FlacMd5State.VALID, "Repaired file should have valid MD5"
            assert not ID3v1HeaderVerifier.has_id3v1_header(
                Path(fixed_file_path)
            ), "ID3v1 tags should be removed during repair"

    def test_fix_md5_checking_warns_about_id3v1_removal(self):
        """Test that fix_md5_checking warns when ID3v1 tags will be removed."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")

            # Verify file has ID3v1 tags
            assert ID3v1HeaderVerifier.has_id3v1_header(test_file), "File should have ID3v1 header"

            # Capture warnings during repair
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")  # Ensure all warnings are captured
                fix_md5_checking(test_file)

            # Verify warning was issued
            assert len(warning_list) == 1, f"Expected 1 warning, got {len(warning_list)}"
            warning = warning_list[0]
            assert issubclass(warning.category, UserWarning), f"Expected UserWarning, got {warning.category}"
            assert "ID3v1 tags detected in FLAC file" in str(warning.message)
            assert "will be removed during MD5 repair" in str(warning.message)
            assert "Consider backing up ID3v1 metadata" in str(warning.message)
