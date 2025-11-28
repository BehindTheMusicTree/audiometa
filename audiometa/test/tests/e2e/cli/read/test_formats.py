import json
import subprocess
import sys

import pytest


@pytest.mark.e2e
class TestCLIReadFormats:
    def test_cli_read_output_formats_json(self, sample_mp3_file):
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(sample_mp3_file), "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "unified_metadata" in data

    def test_cli_read_output_formats_table(self, sample_mp3_file):
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(sample_mp3_file), "--format", "table"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert "UNIFIED METADATA" in result.stdout or "TECHNICAL INFO" in result.stdout

    def test_cli_read_output_formats_yaml(self, sample_mp3_file):
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(sample_mp3_file), "--format", "yaml"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0

    def test_cli_output_to_file(self, sample_mp3_file, tmp_path):
        output_file = tmp_path / "metadata.json"
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(sample_mp3_file), "--output", str(output_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert output_file.exists()

        with output_file.open() as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert "unified_metadata" in data
