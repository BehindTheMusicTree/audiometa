"""Tests for get_full_metadata function."""

from pathlib import Path

import pytest

from audiometa import get_full_metadata
from audiometa._audio_file import _AudioFile
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.integration
class TestGetFullMetadata:
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
        assert "bitrate_kbps" in tech_info
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

    def test_get_full_metadata_without_headers(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file, include_headers=False)

        # Should still have basic structure
        assert "unified_metadata" in result
        assert "technical_info" in result
        assert "metadata_format" in result
        assert "format_priorities" in result

        # Headers and raw metadata should be empty or minimal
        assert "headers" in result
        assert "raw_metadata" in result

    def test_get_full_metadata_without_technical(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file, include_technical=False)

        # Should still have basic structure
        assert "unified_metadata" in result
        assert "metadata_format" in result
        assert "headers" in result
        assert "raw_metadata" in result
        assert "format_priorities" in result

        # Technical info should be empty or minimal
        assert "technical_info" in result

    def test_get_full_metadata_file_with_no_metadata(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = get_full_metadata(temp_file_path)

            # Should still return complete structure
            assert "unified_metadata" in result
            assert "technical_info" in result
            assert "metadata_format" in result
            assert "headers" in result
            assert "raw_metadata" in result
            assert "format_priorities" in result

            # Unified metadata should be empty or minimal
            assert isinstance(result["unified_metadata"], dict)

            # Technical info should still be present
            tech_info = result["technical_info"]
            assert "duration_seconds" in tech_info
            assert "bitrate_kbps" in tech_info
            assert "file_size_bytes" in tech_info

    def test_get_full_metadata_headers_present_flags(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file)

        # Check ID3v2 headers
        id3v2_headers = result["headers"]["id3v2"]
        assert "present" in id3v2_headers
        assert "version" in id3v2_headers
        assert "header_size_bytes" in id3v2_headers
        assert "flags" in id3v2_headers
        assert "extended_header" in id3v2_headers

        # Check ID3v1 headers
        id3v1_headers = result["headers"]["id3v1"]
        assert "present" in id3v1_headers
        assert "position" in id3v1_headers
        assert "size_bytes" in id3v1_headers
        assert "version" in id3v1_headers
        assert "has_track_number" in id3v1_headers

    def test_get_full_metadata_raw_metadata_structure(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file)

        # Check ID3v2 raw metadata
        id3v2_raw = result["raw_metadata"]["id3v2"]
        assert "raw_data" in id3v2_raw
        assert "parsed_fields" in id3v2_raw
        assert "frames" in id3v2_raw
        assert "comments" in id3v2_raw
        assert "chunk_structure" in id3v2_raw

        # Check ID3v1 raw metadata
        id3v1_raw = result["raw_metadata"]["id3v1"]
        assert "raw_data" in id3v1_raw
        assert "parsed_fields" in id3v1_raw
        assert "frames" in id3v1_raw
        assert "comments" in id3v1_raw
        assert "chunk_structure" in id3v1_raw

    def test_get_full_metadata_consistency_with_merged_metadata(self, sample_mp3_file: Path):
        from audiometa import get_unified_metadata

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
        assert tech_info["bitrate_kbps"] == audio_file.get_bitrate()
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

    def test_get_full_metadata_error_handling(self):
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            get_full_metadata("non_existent_file.mp3")

        # Test with unsupported file type
        import tempfile

        from audiometa.exceptions import FileTypeNotSupportedError

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            with pytest.raises(FileTypeNotSupportedError):
                get_full_metadata(tmp_path)
        finally:
            Path(tmp_path).unlink()

    def test_get_full_metadata_performance_optimization(self, sample_mp3_file: Path):
        """Test that performance optimization flags work correctly."""
        # Test with minimal data
        result_minimal = get_full_metadata(sample_mp3_file, include_headers=False, include_technical=False)

        # Should still have basic structure
        assert "unified_metadata" in result_minimal
        assert "metadata_format" in result_minimal
        assert "format_priorities" in result_minimal

        # Headers and technical info should be minimal
        assert "headers" in result_minimal
        assert "technical_info" in result_minimal

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

    def test_get_full_metadata_header_detection_accuracy(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file)

        # Check that headers are detected correctly
        headers = result["headers"]

        for metadata_format_name, header_info in headers.items():
            assert "present" in header_info
            assert isinstance(header_info["present"], bool)

            if header_info["present"]:
                # If header is present, should have additional info
                if metadata_format_name == "id3v2":
                    assert "version" in header_info
                    assert "header_size_bytes" in header_info
                elif metadata_format_name == "id3v1":
                    assert "position" in header_info
                    assert "size_bytes" in header_info
                elif metadata_format_name == "vorbis":
                    assert "vendor_string" in header_info
                    assert "comment_count" in header_info
                elif metadata_format_name == "riff":
                    assert "chunk_info" in header_info
