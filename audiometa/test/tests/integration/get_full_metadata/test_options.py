"""Tests for get_full_metadata function options (include_headers, include_technical)."""

from pathlib import Path

import pytest

from audiometa import get_full_metadata


@pytest.mark.integration
class TestGetFullMetadataOptions:
    def test_get_full_metadata_exclude_headers(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file, include_headers=False)

        # Should include basic structure
        assert "unified_metadata" in result
        assert "technical_info" in result
        assert "metadata_format" in result
        assert "format_priorities" in result

        # Headers should be empty dict when excluded
        assert "headers" in result
        assert result["headers"] == {}

        # Raw metadata should be empty dict when excluded
        assert "raw_metadata" in result
        assert result["raw_metadata"] == {}

        # Verify technical info is still included
        assert result["technical_info"] != {}
        assert "duration_seconds" in result["technical_info"]
        assert "bitrate_kbps" in result["technical_info"]

        # Verify unified metadata is still included
        assert isinstance(result["unified_metadata"], dict)

        # Verify format metadata is still included
        assert isinstance(result["metadata_format"], dict)
        assert "id3v2" in result["metadata_format"]
        assert "id3v1" in result["metadata_format"]

    def test_get_full_metadata_exclude_technical(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file, include_technical=False)

        # Should include basic structure
        assert "unified_metadata" in result
        assert "metadata_format" in result
        assert "headers" in result
        assert "raw_metadata" in result
        assert "format_priorities" in result

        # Technical info should be empty dict when excluded
        assert "technical_info" in result
        assert result["technical_info"] == {}

        # Verify headers are still included
        assert result["headers"] != {}
        assert "id3v2" in result["headers"]
        assert "id3v1" in result["headers"]

        # Verify raw metadata is still included
        assert result["raw_metadata"] != {}
        assert "id3v2" in result["raw_metadata"]
        assert "id3v1" in result["raw_metadata"]

        # Verify unified metadata is still included
        assert isinstance(result["unified_metadata"], dict)

        # Verify format metadata is still included
        assert isinstance(result["metadata_format"], dict)

    def test_get_full_metadata_exclude_both_headers_and_technical(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file, include_headers=False, include_technical=False)

        # Should include basic structure
        assert "unified_metadata" in result
        assert "metadata_format" in result
        assert "format_priorities" in result

        # Headers should be empty dict when excluded
        assert "headers" in result
        assert result["headers"] == {}

        # Raw metadata should be empty dict when excluded
        assert "raw_metadata" in result
        assert result["raw_metadata"] == {}

        # Technical info should be empty dict when excluded
        assert "technical_info" in result
        assert result["technical_info"] == {}

        # Verify unified metadata is still included
        assert isinstance(result["unified_metadata"], dict)

        # Verify format metadata is still included
        assert isinstance(result["metadata_format"], dict)

    def test_get_full_metadata_exclude_headers_flac(self, sample_flac_file: Path):
        result = get_full_metadata(sample_flac_file, include_headers=False)

        # Should include basic structure
        assert "unified_metadata" in result
        assert "technical_info" in result
        assert "metadata_format" in result
        assert "format_priorities" in result

        # Headers should be empty dict when excluded
        assert "headers" in result
        assert result["headers"] == {}

        # Raw metadata should be empty dict when excluded
        assert "raw_metadata" in result
        assert result["raw_metadata"] == {}

        # Verify technical info is still included
        assert result["technical_info"] != {}
        assert "is_flac_md5_valid" in result["technical_info"]

        # Verify format metadata is still included
        assert isinstance(result["metadata_format"], dict)
        assert "vorbis" in result["metadata_format"]

    def test_get_full_metadata_exclude_technical_flac(self, sample_flac_file: Path):
        result = get_full_metadata(sample_flac_file, include_technical=False)

        # Should include basic structure
        assert "unified_metadata" in result
        assert "metadata_format" in result
        assert "headers" in result
        assert "raw_metadata" in result
        assert "format_priorities" in result

        # Technical info should be empty dict when excluded
        assert "technical_info" in result
        assert result["technical_info"] == {}

        # Verify headers are still included
        assert result["headers"] != {}
        assert "vorbis" in result["headers"]

        # Verify raw metadata is still included
        assert result["raw_metadata"] != {}
        assert "vorbis" in result["raw_metadata"]

    def test_get_full_metadata_exclude_headers_wav(self, sample_wav_file: Path):
        result = get_full_metadata(sample_wav_file, include_headers=False)

        # Should include basic structure
        assert "unified_metadata" in result
        assert "technical_info" in result
        assert "metadata_format" in result
        assert "format_priorities" in result

        # Headers should be empty dict when excluded
        assert "headers" in result
        assert result["headers"] == {}

        # Raw metadata should be empty dict when excluded
        assert "raw_metadata" in result
        assert result["raw_metadata"] == {}

        # Verify technical info is still included
        assert result["technical_info"] != {}
        assert result["technical_info"]["file_extension"] == ".wav"

        # Verify format metadata is still included
        assert isinstance(result["metadata_format"], dict)
        assert "riff" in result["metadata_format"]

    def test_get_full_metadata_exclude_technical_wav(self, sample_wav_file: Path):
        result = get_full_metadata(sample_wav_file, include_technical=False)

        # Should include basic structure
        assert "unified_metadata" in result
        assert "metadata_format" in result
        assert "headers" in result
        assert "raw_metadata" in result
        assert "format_priorities" in result

        # Technical info should be empty dict when excluded
        assert "technical_info" in result
        assert result["technical_info"] == {}

        # Verify headers are still included
        assert result["headers"] != {}
        assert "riff" in result["headers"]

        # Verify raw metadata is still included
        assert result["raw_metadata"] != {}
        assert "riff" in result["raw_metadata"]

    def test_get_full_metadata_exclude_options(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file, include_headers=False, include_technical=False)

        # Should work the same as with path
        assert "unified_metadata" in result
        assert "metadata_format" in result
        assert "format_priorities" in result

        # Excluded sections should be empty
        assert result["headers"] == {}
        assert result["raw_metadata"] == {}
        assert result["technical_info"] == {}

        # Included sections should have data
        assert isinstance(result["unified_metadata"], dict)
        assert isinstance(result["metadata_format"], dict)
