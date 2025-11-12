from pathlib import Path

import pytest

from audiometa import get_full_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestParsedFieldsKeys:
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
