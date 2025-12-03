"""Test MD5 validation with all metadata format combinations (VALID, UNCHECKABLE, etc.)."""

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import ensure_flac_has_md5


@pytest.mark.integration
class TestMd5WithMetadataCombinations:
    """Test MD5 validation with all metadata format combinations."""

    def test_valid_md5_no_metadata(self):
        """Test VALID state with no metadata (clean FLAC)."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.VALID, "Clean FLAC with valid MD5 should return VALID"

    def test_valid_md5_vorbis_only(self):
        """Test VALID state with Vorbis metadata only."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            VorbisMetadataSetter.set_artist(test_file, "Vorbis Artist")
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.VALID, "FLAC with Vorbis metadata only should return VALID"

    def test_valid_md5_id3v2_only(self):
        """Test VALID state with ID3v2 metadata only."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title", "artist": "ID3v2 Artist"})
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.VALID, "FLAC with ID3v2 metadata only should return VALID"

    def test_uncheckable_md5_id3v1_only(self):
        """Test UNCHECKABLE_DUE_TO_ID3 state with ID3v1 metadata only."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v1MetadataSetter.set_artist(test_file, "ID3v1 Artist")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "FLAC with ID3v1 metadata only should return UNCHECKABLE_DUE_TO_ID3"

    def test_valid_md5_vorbis_and_id3v2(self):
        """Test VALID state with Vorbis and ID3v2 metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title", "artist": "ID3v2 Artist"})
            state = is_flac_md5_valid(test_file)
            assert state == FlacMd5State.VALID, "FLAC with Vorbis and ID3v2 metadata should return VALID"

    def test_uncheckable_md5_vorbis_and_id3v1(self):
        """Test UNCHECKABLE_DUE_TO_ID3 state with Vorbis and ID3v1 metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v1MetadataSetter.set_artist(test_file, "ID3v1 Artist")
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "FLAC with Vorbis and ID3v1 metadata should return UNCHECKABLE_DUE_TO_ID3"

    def test_uncheckable_md5_id3v1_and_id3v2(self):
        """Test UNCHECKABLE_DUE_TO_ID3 state with ID3v1 and ID3v2 metadata."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title", "artist": "ID3v2 Artist"})
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "FLAC with ID3v1 and ID3v2 metadata should return UNCHECKABLE_DUE_TO_ID3"

    def test_uncheckable_md5_vorbis_id3v1_and_id3v2(self):
        """Test UNCHECKABLE_DUE_TO_ID3 state with all metadata formats."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title", "artist": "ID3v2 Artist"})
            state = is_flac_md5_valid(test_file)
            assert (
                state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1
            ), "FLAC with all metadata formats should return UNCHECKABLE_DUE_TO_ID3 (ID3v1 present)"
