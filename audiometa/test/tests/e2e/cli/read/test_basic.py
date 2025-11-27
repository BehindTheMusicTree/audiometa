import json
import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIReadBasic:
    def test_cli_read_nonexistent_file(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.mp3"
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(nonexistent_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 1
        assert "error" in result.stderr.lower()

    def test_cli_read_with_continue_on_error(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.mp3"
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(nonexistent_file), "--continue-on-error"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0

    def test_cli_with_spaces_in_filename(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert isinstance(data, dict)
            assert "unified_metadata" in data

    def test_cli_read_basic_metadata(self):
        with temp_file_with_metadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert "unified_metadata" in data
            assert data["unified_metadata"].get("title") == "Test Title"
            assert data["unified_metadata"].get("artists") == ["Test Artist"]
