"""Tests for get_full_metadata function consistency and accuracy."""

from pathlib import Path

import pytest

from audiometa import get_full_metadata, get_unified_metadata
from audiometa._audio_file import _AudioFile


@pytest.mark.integration
class TestGetFullMetadataConsistency:
    def test_get_full_metadata_consistency_with_merged_metadata(self, sample_mp3_file: Path):
        full_result = get_full_metadata(sample_mp3_file)
        merged_result = get_unified_metadata(sample_mp3_file)

        # Should be identical
        assert full_result["unified_metadata"] == merged_result

    def test_get_full_metadata_technical_info_accuracy(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        result = get_full_metadata(sample_mp3_file)

        tech_info = result["technical_info"]

        # Compare with direct _AudioFile methods
        assert tech_info["duration_seconds"] == audio_file.get_duration_in_sec()
        assert tech_info["bitrate_bps"] == audio_file.get_bitrate()
        assert tech_info["sample_rate_hz"] == audio_file.get_sample_rate()
        assert tech_info["channels"] == audio_file.get_channels()
        assert tech_info["file_size_bytes"] == audio_file.get_file_size()
        assert tech_info["file_extension"] == audio_file.file_extension
        assert tech_info["audio_format_name"] == audio_file.get_audio_format_name()

    def test_get_full_metadata_flac_md5_validation(self, sample_flac_file: Path):
        result = get_full_metadata(sample_flac_file)

        tech_info = result["technical_info"]
        assert "is_flac_md5_valid" in tech_info
        assert isinstance(tech_info["is_flac_md5_valid"], bool)

    def test_get_full_metadata_structure_consistency(self, sample_mp3_file: Path):
        result1 = get_full_metadata(sample_mp3_file)
        result2 = get_full_metadata(sample_mp3_file)

        # Structure should be identical
        assert set(result1.keys()) == set(result2.keys())

        # Each top-level section should have same keys
        for key in result1:
            if key in ["unified_metadata", "technical_info", "metadata_format", "headers", "raw_metadata"]:
                assert set(result1[key].keys()) == set(result2[key].keys())

    def test_get_full_metadata_format_detection_accuracy(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file)

        # Format priorities should be correct for MP3
        priorities = result["format_priorities"]
        assert priorities["file_extension"] == ".mp3"
        assert "id3v2" in priorities["reading_order"]
        assert "id3v1" in priorities["reading_order"]
        assert priorities["writing_format"] == "id3v2"

        # Technical info should reflect MP3 format
        tech_info = result["technical_info"]
        assert tech_info["file_extension"] == ".mp3"
        assert tech_info["audio_format_name"] == "MP3"
