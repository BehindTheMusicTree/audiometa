import json
import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIReadOptions:
    def test_cli_read_no_headers(self):
        with temp_file_with_metadata({"title": "Test Title"}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(test_file), "--no-headers", "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert "unified_metadata" in data
            # When --no-headers is used, headers should be empty dict, not absent
            assert "headers" in data
            assert data["headers"] == {}

    def test_cli_read_no_technical(self):
        with temp_file_with_metadata({"title": "Test Title"}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(test_file), "--no-technical", "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert "unified_metadata" in data
            # When --no-technical is used, technical_info should be empty dict, not absent
            assert "technical_info" in data
            assert data["technical_info"] == {}

    def test_cli_read_no_headers_no_technical(self):
        with temp_file_with_metadata({"title": "Test Title"}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "read",
                    str(test_file),
                    "--no-headers",
                    "--no-technical",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert "unified_metadata" in data
            # When --no-headers and --no-technical are used, these should be empty dicts, not absent
            assert "headers" in data
            assert data["headers"] == {}
            assert "technical_info" in data
            assert data["technical_info"] == {}

    def test_cli_read_with_all_options(self):
        with temp_file_with_metadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "read",
                    str(test_file),
                    "--no-headers",
                    "--no-technical",
                    "--format",
                    "table",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "UNIFIED METADATA" in result.stdout
