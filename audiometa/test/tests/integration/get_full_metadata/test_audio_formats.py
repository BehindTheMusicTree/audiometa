"""Tests for get_full_metadata function with different audio formats."""

from pathlib import Path

import pytest

from audiometa import get_full_metadata


@pytest.mark.integration
class TestGetFullMetadataAudioFormats:
    def test_get_full_metadata_mp3_with_metadata(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file)

        # Check structure
        assert "unified_metadata" in result
        assert "technical_info" in result
        assert "metadata_format" in result
        assert "headers" in result
        assert "raw_metadata" in result
        assert "format_priorities" in result

        # Check format priorities
        assert result["format_priorities"]["file_extension"] == ".mp3"
        assert "id3v2" in result["format_priorities"]["reading_order"]
        assert "id3v1" in result["format_priorities"]["reading_order"]
        assert result["format_priorities"]["writing_format"] == "id3v2"

        # Check technical info
        tech_info = result["technical_info"]
        assert "duration_seconds" in tech_info
        assert "bitrate_bps" in tech_info
        assert "sample_rate_hz" in tech_info
        assert "channels" in tech_info
        assert "file_size_bytes" in tech_info
        assert "file_extension" in tech_info
        assert "audio_format_name" in tech_info
        assert tech_info["file_extension"] == ".mp3"
        assert tech_info["audio_format_name"] == "MP3"
        assert tech_info["is_flac_md5_valid"] is None  # Not a FLAC file

        # Check format metadata
        assert "id3v2" in result["metadata_format"]
        assert "id3v1" in result["metadata_format"]

        # Check headers
        assert "id3v2" in result["headers"]
        assert "id3v1" in result["headers"]

        # Check raw metadata
        assert "id3v2" in result["raw_metadata"]
        assert "id3v1" in result["raw_metadata"]

    def test_get_full_metadata_flac_with_metadata(self, sample_flac_file: Path):
        result = get_full_metadata(sample_flac_file)

        # Check format priorities
        assert result["format_priorities"]["file_extension"] == ".flac"
        assert "vorbis" in result["format_priorities"]["reading_order"]
        assert "id3v2" in result["format_priorities"]["reading_order"]
        assert "id3v1" in result["format_priorities"]["reading_order"]
        assert result["format_priorities"]["writing_format"] == "vorbis"

        # Check technical info
        tech_info = result["technical_info"]
        assert tech_info["file_extension"] == ".flac"
        assert tech_info["audio_format_name"] == "FLAC"
        assert "is_flac_md5_valid" in tech_info  # Should be present for FLAC

        # Check format metadata
        assert "vorbis" in result["metadata_format"]
        assert "id3v2" in result["metadata_format"]
        assert "id3v1" in result["metadata_format"]

        # Check headers
        assert "vorbis" in result["headers"]
        assert "id3v2" in result["headers"]
        assert "id3v1" in result["headers"]

    def test_get_full_metadata_wav_with_metadata(self, sample_wav_file: Path):
        result = get_full_metadata(sample_wav_file)

        # Check format priorities
        assert result["format_priorities"]["file_extension"] == ".wav"
        assert "riff" in result["format_priorities"]["reading_order"]
        assert "id3v2" in result["format_priorities"]["reading_order"]
        assert "id3v1" in result["format_priorities"]["reading_order"]
        assert result["format_priorities"]["writing_format"] == "riff"

        # Check technical info
        tech_info = result["technical_info"]
        assert tech_info["file_extension"] == ".wav"
        assert tech_info["audio_format_name"] == "WAV"
        assert tech_info["is_flac_md5_valid"] is None  # Not a FLAC file

        # Check format metadata
        assert "riff" in result["metadata_format"]
        assert "id3v2" in result["metadata_format"]
        assert "id3v1" in result["metadata_format"]

        # Check headers
        assert "riff" in result["headers"]
        assert "id3v2" in result["headers"]
        assert "id3v1" in result["headers"]

    def test_get_full_metadata_format_specific_metadata_isolation(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file)

        # Each format should have its own metadata section
        metadata_format = result["metadata_format"]

        # ID3v2 metadata should be separate from ID3v1
        if "id3v2" in metadata_format and "id3v1" in metadata_format:
            id3v2_metadata = metadata_format["id3v2"]
            id3v1_metadata = metadata_format["id3v1"]

            # They should be separate dictionaries
            assert isinstance(id3v2_metadata, dict)
            assert isinstance(id3v1_metadata, dict)

            # They might have different content or structure
            # This is expected and correct behavior
