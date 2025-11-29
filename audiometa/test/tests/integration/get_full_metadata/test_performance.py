"""Performance tests for get_full_metadata function."""

import threading
from pathlib import Path

import pytest

from audiometa import get_full_metadata


@pytest.mark.integration
class TestGetFullMetadataPerformance:
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
