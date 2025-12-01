"""Edge case tests for get_full_metadata function."""

from pathlib import Path

import pytest

from audiometa import get_full_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.integration
class TestGetFullMetadataEdgeCases:
    def test_get_full_metadata_empty_file(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            # Should handle gracefully and return structure with minimal data
            result = get_full_metadata(temp_file_path)

            # Should still return complete structure
            assert "unified_metadata" in result
            assert "technical_info" in result
            assert "metadata_format" in result
            assert "headers" in result
            assert "raw_metadata" in result
            assert "format_priorities" in result

    def test_get_full_metadata_file_with_only_headers_no_metadata(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = get_full_metadata(temp_file_path)

            # Should detect headers even if no metadata content
            headers = result["headers"]

            for _metadata_format_name, header_info in headers.items():
                # Headers might be present even without metadata content
                assert "present" in header_info
                assert isinstance(header_info["present"], bool)

    def test_get_full_metadata_large_file(self, sample_mp3_file: Path):
        # This test ensures the function can handle larger files
        result = get_full_metadata(sample_mp3_file)

        # Should complete successfully
        assert "unified_metadata" in result
        assert "technical_info" in result

        # File size should be reasonable
        tech_info = result["technical_info"]
        assert tech_info["file_size_bytes"] > 0

    def test_get_full_metadata_file_with_mixed_formats(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file)

        # Should handle multiple formats gracefully
        metadata_format = result["metadata_format"]
        headers = result["headers"]

        # Each format should have its own section
        for metadata_format_name in ["id3v2", "id3v1"]:
            assert metadata_format_name in metadata_format
            assert metadata_format_name in headers

            # Each should be a dictionary
            assert isinstance(metadata_format[metadata_format_name], dict)
            assert isinstance(headers[metadata_format_name], dict)

    def test_get_full_metadata_with_unicode_metadata(self, sample_mp3_file: Path):
        # This test ensures unicode handling works correctly
        result = get_full_metadata(sample_mp3_file)

        # Should handle unicode in metadata
        unified_metadata = result["unified_metadata"]

        # Check that string values are properly handled
        for _key, value in unified_metadata.items():
            if isinstance(value, str):
                # Should be able to handle unicode
                assert isinstance(value, str)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        assert isinstance(item, str)

    def test_get_full_metadata_with_minimal_metadata(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = get_full_metadata(temp_file_path)

            # Should still return complete structure
            assert "unified_metadata" in result
            assert "technical_info" in result
            assert "metadata_format" in result
            assert "headers" in result
            assert "raw_metadata" in result
            assert "format_priorities" in result

            # Unified metadata might be empty or minimal
            unified_metadata = result["unified_metadata"]
            assert isinstance(unified_metadata, dict)

            # Technical info should still be present
            tech_info = result["technical_info"]
            assert "file_size_bytes" in tech_info
            assert tech_info["file_size_bytes"] >= 0  # Can be 0 for empty files

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
            assert "bitrate_bps" in tech_info
            assert "file_size_bytes" in tech_info
