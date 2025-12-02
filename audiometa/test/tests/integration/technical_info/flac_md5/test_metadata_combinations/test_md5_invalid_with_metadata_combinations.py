"""Test INVALID MD5 state with metadata format combinations that support validation."""

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import corrupt_md5, ensure_flac_has_md5


@pytest.mark.integration
class TestMd5InvalidWithMetadataCombinations:
    """Test INVALID MD5 state with metadata format combinations that support validation."""

    def test_invalid_md5_no_metadata(self):
        """Test INVALID state with no metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.INVALID, "Clean FLAC with invalid MD5 should return INVALID"

    def test_invalid_md5_vorbis_only(self):
        """Test INVALID state with Vorbis metadata only."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.INVALID, "FLAC with Vorbis metadata and invalid MD5 should return INVALID"

    def test_invalid_md5_id3v2_only(self):
        """Test INVALID state with ID3v2 metadata only."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.INVALID, "FLAC with ID3v2 metadata and invalid MD5 should return INVALID"

    def test_invalid_md5_vorbis_and_id3v2(self):
        """Test INVALID state with Vorbis and ID3v2 metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.INVALID
            ), "FLAC with Vorbis and ID3v2 metadata and invalid MD5 should return INVALID"

    def test_invalid_md5_with_id3v1_returns_uncheckable(self):
        """Test that invalid MD5 with ID3v1 returns UNCHECKABLE_DUE_TO_ID3, not INVALID."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "FLAC with ID3v1 should return UNCHECKABLE_DUE_TO_ID3 even if MD5 corrupted (ID3v1 takes precedence)"

    def test_invalid_md5_vorbis_and_id3v1_returns_uncheckable(self):
        """Test that invalid MD5 with Vorbis and ID3v1 returns UNCHECKABLE_DUE_TO_ID3."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "FLAC with Vorbis and ID3v1 metadata should return UNCHECKABLE_DUE_TO_ID3 (ID3v1 takes precedence)"

    def test_invalid_md5_id3v1_and_id3v2_returns_uncheckable(self):
        """Test that invalid MD5 with ID3v1 and ID3v2 returns UNCHECKABLE_DUE_TO_ID3."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "FLAC with ID3v1 and ID3v2 metadata should return UNCHECKABLE_DUE_TO_ID3 (ID3v1 takes precedence)"

    def test_invalid_md5_all_formats_returns_uncheckable(self):
        """Test that invalid MD5 with all metadata formats returns UNCHECKABLE_DUE_TO_ID3."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "FLAC with all metadata formats should return UNCHECKABLE_DUE_TO_ID3 (ID3v1 takes precedence)"
