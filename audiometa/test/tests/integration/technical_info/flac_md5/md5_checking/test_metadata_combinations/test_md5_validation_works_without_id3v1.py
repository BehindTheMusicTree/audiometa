"""Test that MD5 validation works correctly when ID3v1 tags are NOT present."""

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import corrupt_md5, ensure_flac_has_md5


@pytest.mark.integration
class TestMd5ValidationWorksWithoutId3v1:
    """Test that MD5 validation works correctly when ID3v1 tags are NOT present.

    These tests confirm that validation works (returns VALID or INVALID based on actual MD5 state)
    for all metadata combinations that do NOT include ID3v1 tags.
    """

    def test_validation_works_no_metadata(self):
        """Test that validation works with no metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.VALID, "Validation should work with no metadata"

    def test_validation_works_vorbis_only(self):
        """Test that validation works with Vorbis metadata only."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.VALID, "Validation should work with Vorbis metadata only"

    def test_validation_works_id3v2_only(self):
        """Test that validation works with ID3v2 metadata only."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.VALID, "Validation should work with ID3v2 metadata only"

    def test_validation_works_vorbis_and_id3v2(self):
        """Test that validation works with Vorbis and ID3v2 metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.VALID, "Validation should work with Vorbis and ID3v2 metadata"

    def test_validation_detects_invalid_without_id3v1(self):
        """Test that validation correctly detects INVALID state without ID3v1."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            corrupt_md5(test_file, "random")
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.INVALID, "Validation should detect INVALID state without ID3v1 tags"
