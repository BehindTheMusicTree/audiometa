import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIWrite:
    def test_cli_write_no_metadata(self, sample_mp3_file):
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "write", str(sample_mp3_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 1
        assert "no metadata fields specified" in result.stderr.lower()

    def test_cli_write_basic_metadata(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(test_file), "--title", "CLI Test Title"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Updated metadata" in result.stdout

    def test_cli_with_spaces_in_filename_write(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "Test Title",
                    "--artist",
                    "Test Artist",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Updated metadata" in result.stdout

    def test_cli_write_rating_integer(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--rating",
                    "50",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Updated metadata" in result.stdout

    def test_cli_invalid_rating_value_fractional_float(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--rating",
                    "1.5",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "invalid" in stderr_output or "error" in stderr_output
            assert "raw mode" in stderr_output or "normalization" in stderr_output

    def test_cli_invalid_rating_value_fractional_float_with_other_metadata(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "Test Song",
                    "--artist",
                    "Test Artist",
                    "--rating",
                    "7.5",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "invalid" in stderr_output or "error" in stderr_output
            assert "raw mode" in stderr_output or "normalization" in stderr_output
