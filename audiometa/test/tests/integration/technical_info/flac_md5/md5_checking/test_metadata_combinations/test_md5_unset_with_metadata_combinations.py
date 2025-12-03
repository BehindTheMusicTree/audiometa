"""Test UNSET MD5 state with all metadata format combinations."""

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import (
    create_flac_without_md5,
    ensure_flac_has_md5,
)


@pytest.mark.integration
class TestMd5UnsetWithMetadataCombinations:
    """Test UNSET MD5 state with all metadata format combinations."""

    def test_unset_md5_no_metadata(self):
        """Test UNSET state with no metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            create_flac_without_md5(test_file)
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.UNSET, "Clean FLAC with unset MD5 should return UNSET"

    def test_unset_md5_vorbis_only(self):
        """Test UNSET state with Vorbis metadata only."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            create_flac_without_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.UNSET, "FLAC with Vorbis metadata and unset MD5 should return UNSET"

    def test_unset_md5_id3v2_only(self):
        """Test UNSET state with ID3v2 metadata only."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            create_flac_without_md5(test_file)
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.UNSET, "FLAC with ID3v2 metadata and unset MD5 should return UNSET"

    def test_unset_md5_id3v1_only(self):
        """Test UNSET state with ID3v1 metadata only (should still be UNSET, not UNCHECKABLE)."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            create_flac_without_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNSET
            ), "FLAC with ID3v1 metadata and unset MD5 should return UNSET (unset takes precedence)"

    def test_unset_md5_vorbis_and_id3v2(self):
        """Test UNSET state with Vorbis and ID3v2 metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            create_flac_without_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.UNSET, "FLAC with Vorbis and ID3v2 metadata and unset MD5 should return UNSET"

    def test_unset_md5_vorbis_and_id3v1(self):
        """Test UNSET state with Vorbis and ID3v1 metadata (unset takes precedence)."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            create_flac_without_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNSET
            ), "FLAC with Vorbis and ID3v1 metadata and unset MD5 should return UNSET (unset takes precedence)"

    def test_unset_md5_id3v1_and_id3v2(self):
        """Test UNSET state with ID3v1 and ID3v2 metadata (unset takes precedence)."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            create_flac_without_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNSET
            ), "FLAC with ID3v1 and ID3v2 metadata and unset MD5 should return UNSET (unset takes precedence)"

    def test_unset_md5_all_formats(self):
        """Test UNSET state with all metadata formats (unset takes precedence)."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            create_flac_without_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNSET
            ), "FLAC with all metadata formats and unset MD5 should return UNSET (unset takes precedence)"
