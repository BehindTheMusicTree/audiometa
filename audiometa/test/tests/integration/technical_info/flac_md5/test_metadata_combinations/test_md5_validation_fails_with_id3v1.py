"""Test that MD5 validation returns UNCHECKABLE_DUE_TO_ID3 when ID3v1 tags are present."""

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import ensure_flac_has_md5


@pytest.mark.integration
class TestMd5ValidationFailsWithId3v1:
    """Test that MD5 validation returns UNCHECKABLE_DUE_TO_ID3 when ID3v1 tags are present.

    These tests confirm that validation fails (returns UNCHECKABLE_DUE_TO_ID3) for all
    metadata combinations that include ID3v1 tags, regardless of other metadata formats.
    """

    def test_validation_fails_id3v1_only(self):
        """Test that validation fails with ID3v1 metadata only."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1, "Validation should fail with ID3v1 metadata only"

    def test_validation_fails_vorbis_and_id3v1(self):
        """Test that validation fails with Vorbis and ID3v1 metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "Validation should fail with Vorbis and ID3v1 metadata"

    def test_validation_fails_id3v1_and_id3v2(self):
        """Test that validation fails with ID3v1 and ID3v2 metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "Validation should fail with ID3v1 and ID3v2 metadata"

    def test_validation_fails_all_formats(self):
        """Test that validation fails with all metadata formats (ID3v1 present)."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "Validation should fail with all metadata formats when ID3v1 is present"
