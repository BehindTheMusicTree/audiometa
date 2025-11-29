"""Tests for get_full_metadata function structure validation."""

from pathlib import Path

import pytest

from audiometa import get_full_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestGetFullMetadataStructure:
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

    def test_get_full_metadata_riff_raw_metadata_structure(self, sample_wav_file: Path):
        """Test RIFF raw metadata structure in get_full_metadata."""
        result = get_full_metadata(sample_wav_file)

        # Check RIFF raw metadata
        riff_raw = result["raw_metadata"]["riff"]
        assert "raw_data" in riff_raw
        assert "parsed_fields" in riff_raw
        assert "frames" in riff_raw
        assert "comments" in riff_raw
        assert "chunk_structure" in riff_raw

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

    def test_id3v1_parsed_fields_use_unified_keys(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file)

        id3v1_raw = result.get("raw_metadata", {}).get("id3v1", {})
        parsed_fields = id3v1_raw.get("parsed_fields", {})

        # If there are parsed fields, they should use UnifiedMetadataKey enum values as keys
        for key in parsed_fields:
            assert isinstance(
                key, UnifiedMetadataKey
            ), f"ID3v1 parsed_fields key {key} should be UnifiedMetadataKey enum, got {type(key)}"
            # Verify it's a valid UnifiedMetadataKey value
            assert key in UnifiedMetadataKey, f"ID3v1 parsed_fields key {key} is not a valid UnifiedMetadataKey"

    def test_riff_parsed_fields_use_raw_keys(self, sample_wav_file: Path):
        result = get_full_metadata(sample_wav_file)

        riff_raw = result.get("raw_metadata", {}).get("riff", {})
        parsed_fields = riff_raw.get("parsed_fields", {})

        # RIFF should use raw RIFF tag keys (like 'INAM', 'IART', etc.)
        # These are NOT UnifiedMetadataKey enum values, which is correct for RIFF
        for key in parsed_fields:
            assert isinstance(key, str), f"RIFF parsed_fields key {key} should be string, got {type(key)}"
            # RIFF keys should be 4-character codes like 'INAM', 'IART', etc.
            assert len(key) == 4, f"RIFF parsed_fields key {key} should be 4 characters (FourCC), got {len(key)}"

    def test_cli_output_parsed_fields_keys(self, sample_mp3_file: Path):
        import json
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(sample_mp3_file), "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        data = json.loads(result.stdout)
        raw_metadata = data.get("raw_metadata", {})

        # Check ID3v1 parsed_fields keys in CLI output
        id3v1_raw = raw_metadata.get("id3v1", {})
        parsed_fields = id3v1_raw.get("parsed_fields", {})

        for key in parsed_fields:
            # In JSON output, UnifiedMetadataKey enum values are serialized as their string values
            # (e.g., "title" instead of "UnifiedMetadataKey.TITLE") because UnifiedMetadataKey inherits from str
            assert isinstance(key, str), f"ID3v1 parsed_fields key in CLI output should be string, got: {type(key)}"

            # Verify it's a valid UnifiedMetadataKey value
            assert key in [
                e.value for e in UnifiedMetadataKey
            ], f"ID3v1 parsed_fields key {key} is not a valid UnifiedMetadataKey value"

    def test_parsed_fields_consistency_across_formats(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file)

        raw_metadata = result.get("raw_metadata", {})

        # Check that all formats have the expected structure
        for metadata_format_name, format_data in raw_metadata.items():
            assert "parsed_fields" in format_data, f"Format {metadata_format_name} should have parsed_fields"
            assert isinstance(
                format_data["parsed_fields"], dict
            ), f"Format {metadata_format_name} parsed_fields should be a dictionary"

            # Check that parsed_fields values are strings (no binary data)
            for key, value in format_data["parsed_fields"].items():
                assert isinstance(
                    value, str
                ), f"Format {metadata_format_name} parsed_fields value for {key} should be string, got {type(value)}"
