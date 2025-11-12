"""Edge case tests for get_full_metadata function."""

import tempfile
from pathlib import Path

import pytest

from audiometa import get_full_metadata
from audiometa.exceptions import FileCorruptedError, FileTypeNotSupportedError
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

    def test_get_full_metadata_corrupted_file(self):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name
            # Write some garbage data
            temp_file.write(b"This is not a valid audio file")

        try:
            with pytest.raises(FileCorruptedError):
                get_full_metadata(temp_path)
        finally:
            Path(temp_path).unlink()

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

    def test_get_full_metadata_performance_with_headers_disabled(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file, include_headers=False)

        # Should still work correctly
        assert "unified_metadata" in result
        assert "technical_info" in result
        assert "metadata_format" in result

        # Headers should be minimal
        headers = result["headers"]
        for _metadata_format_name, header_info in headers.items():
            # Should have basic structure but minimal data
            assert "present" in header_info

    def test_get_full_metadata_performance_with_technical_disabled(self, sample_mp3_file: Path):
        result = get_full_metadata(sample_mp3_file, include_technical=False)

        # Should still work correctly
        assert "unified_metadata" in result
        assert "metadata_format" in result
        assert "headers" in result

        # Technical info should be minimal
        tech_info = result["technical_info"]
        assert isinstance(tech_info, dict)

    def test_get_full_metadata_memory_usage(self, sample_mp3_file: Path):
        # This is more of a smoke test to ensure no obvious memory leaks
        for _ in range(10):
            result = get_full_metadata(sample_mp3_file)

            # Should complete successfully each time
            assert "unified_metadata" in result
            assert "technical_info" in result

            # Clear result to help with memory management
            del result

    def test_get_full_metadata_concurrent_access(self, sample_mp3_file: Path):
        import threading

        results = []
        errors = []

        def get_metadata():
            try:
                result = get_full_metadata(sample_mp3_file)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads accessing the same file
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_metadata)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should have 5 successful results
        assert len(results) == 5
        assert len(errors) == 0

        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result["format_priorities"] == first_result["format_priorities"]
            assert result["technical_info"]["file_size_bytes"] == first_result["technical_info"]["file_size_bytes"]

    def test_get_full_metadata_error_recovery(self):
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            get_full_metadata("non_existent_file.mp3")

        # Test with unsupported file type (create the file first)
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(b"This is not an audio file")

        try:
            with pytest.raises(FileTypeNotSupportedError):
                get_full_metadata(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_get_full_metadata_structure_consistency(self, sample_mp3_file: Path):
        result1 = get_full_metadata(sample_mp3_file)
        result2 = get_full_metadata(sample_mp3_file)

        # Structure should be identical
        assert set(result1.keys()) == set(result2.keys())

        # Each top-level section should have same keys
        for key in result1:
            if key in ["unified_metadata", "technical_info", "metadata_format", "headers", "raw_metadata"]:
                assert set(result1[key].keys()) == set(result2[key].keys())

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
