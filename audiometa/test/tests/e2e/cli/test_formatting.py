import json

import pytest

from audiometa.cli import format_as_table, format_output


@pytest.mark.e2e
class TestCLIFormatting:
    def test_format_output_json(self):
        data = {"title": "Test Song", "artist": "Test Artist"}
        result = format_output(data, "json")
        parsed = json.loads(result)
        assert parsed == data

    def test_format_output_yaml(self):
        data = {"title": "Test Song", "artist": "Test Artist"}
        result = format_output(data, "yaml")
        # Should fall back to JSON if PyYAML not available
        assert "Test Song" in result

    def test_format_output_table(self):
        data = {
            "unified_metadata": {"title": "Test Song", "artist": "Test Artist"},
            "technical_info": {"duration_seconds": 180, "bitrate_kbps": 320},
        }
        result = format_as_table(data)
        assert "Test Song" in result
        assert "Test Artist" in result
        assert "180" in result
        assert "320" in result
