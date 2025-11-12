"""Unit tests for Vorbis metadata manager header information methods."""

from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile
from audiometa.manager._rating_supporting.vorbis._VorbisManager import _VorbisManager as VorbisManager


@pytest.mark.unit
class TestVorbisHeaderMethods:
    """Test cases for Vorbis metadata manager header information methods."""

    def test_vorbis_manager_header_info(self, sample_flac_file: Path):
        """Test VorbisManager header info method."""
        audio_file = _AudioFile(sample_flac_file)
        manager = VorbisManager(audio_file)

        header_info = manager.get_header_info()

        # Should have Vorbis specific structure
        assert "present" in header_info
        assert "vendor_string" in header_info
        assert "comment_count" in header_info
        assert "block_size" in header_info

        # Should be valid structure
        assert isinstance(header_info["present"], bool)
        assert header_info["vendor_string"] is None or isinstance(header_info["vendor_string"], str)
        assert isinstance(header_info["comment_count"], int)
        assert isinstance(header_info["block_size"], int)

    def test_vorbis_manager_raw_metadata_info(self, sample_flac_file: Path):
        """Test VorbisManager raw metadata info method."""
        audio_file = _AudioFile(sample_flac_file)
        manager = VorbisManager(audio_file)

        raw_info = manager.get_raw_metadata_info()

        # Should have Vorbis specific structure
        assert "raw_data" in raw_info
        assert "parsed_fields" in raw_info
        assert "frames" in raw_info
        assert "comments" in raw_info
        assert "chunk_structure" in raw_info

        # Should be valid structure
        assert raw_info["raw_data"] is None or isinstance(raw_info["raw_data"], bytes)
        assert isinstance(raw_info["parsed_fields"], dict)
        assert isinstance(raw_info["frames"], dict)
        assert isinstance(raw_info["comments"], dict)
        assert isinstance(raw_info["chunk_structure"], dict)
