"""Unit tests for RIFF metadata manager header information methods."""

from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile
from audiometa.manager._rating_supporting.riff._RiffManager import _RiffManager as RiffManager


@pytest.mark.unit
class TestRiffHeaderMethods:
    """Test cases for RIFF metadata manager header information methods."""

    def test_riff_manager_header_info(self, sample_wav_file: Path):
        """Test RiffManager header info method."""
        audio_file = _AudioFile(sample_wav_file)
        manager = RiffManager(audio_file)

        header_info = manager.get_header_info()

        # Should have RIFF specific structure
        assert "present" in header_info
        assert "chunk_info" in header_info

        # Should be valid structure
        assert isinstance(header_info["present"], bool)
        assert isinstance(header_info["chunk_info"], dict)

        # Chunk info should have expected keys
        chunk_info = header_info["chunk_info"]
        if header_info["present"]:
            assert "riff_chunk_size" in chunk_info
            assert "info_chunk_size" in chunk_info
            assert "audio_format" in chunk_info
            assert "subchunk_size" in chunk_info

    def test_riff_manager_raw_metadata_info(self, sample_wav_file: Path):
        """Test RiffManager raw metadata info method."""
        audio_file = _AudioFile(sample_wav_file)
        manager = RiffManager(audio_file)

        raw_info = manager.get_raw_metadata_info()

        # Should have RIFF specific structure
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
