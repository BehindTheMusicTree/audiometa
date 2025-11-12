from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile
from audiometa.manager.id3v1._Id3v1Manager import _Id3v1Manager as Id3v1Manager


@pytest.mark.unit
class TestId3v1HeaderMethods:
    def test_id3v1_manager_header_info(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        manager = Id3v1Manager(audio_file)

        header_info = manager.get_header_info()

        # Should have ID3v1 specific structure
        assert "present" in header_info
        assert "position" in header_info
        assert "size_bytes" in header_info
        assert "version" in header_info
        assert "has_track_number" in header_info

        # Should be valid structure
        assert isinstance(header_info["present"], bool)
        assert header_info["position"] is None or isinstance(header_info["position"], str)
        assert isinstance(header_info["size_bytes"], int)
        assert header_info["version"] is None or isinstance(header_info["version"], str)
        assert isinstance(header_info["has_track_number"], bool)

    def test_id3v1_manager_raw_metadata_info(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        manager = Id3v1Manager(audio_file)

        raw_info = manager.get_raw_metadata_info()

        # Should have ID3v1 specific structure
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
