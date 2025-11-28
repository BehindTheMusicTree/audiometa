import json
import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIReadUnified:
    def test_cli_unified_output(self, sample_mp3_file):
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "unified", str(sample_mp3_file), "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert "unified_metadata" not in data
        assert "headers" not in data
        assert "technical_info" not in data

    def test_cli_unified_with_metadata(self):
        with temp_file_with_metadata({"title": "Unified Test", "artist": "Unified Artist"}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "unified", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert isinstance(data, dict)
            assert data.get("title") == "Unified Test"
            assert data.get("artists") == ["Unified Artist"]

    def test_cli_unified_table_format(self):
        with temp_file_with_metadata({"title": "Table Test", "artist": "Table Artist"}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "unified", str(test_file), "--format", "table"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "title" in result.stdout.lower() or "Table Test" in result.stdout

    def test_cli_unified_output_to_file(self, tmp_path):
        with temp_file_with_metadata({"title": "File Test"}, "mp3") as test_file:
            output_file = tmp_path / "unified.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "unified",
                    str(test_file),
                    "--output",
                    str(output_file),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert output_file.exists()
            with output_file.open() as f:
                data = json.load(f)
            assert isinstance(data, dict)

    def test_cli_with_spaces_in_filename_unified(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "unified", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert isinstance(data, dict)
