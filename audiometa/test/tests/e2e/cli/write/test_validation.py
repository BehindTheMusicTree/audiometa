import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIWriteValidation:
    def test_cli_write_negative_disc_number_error(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--disc-number",
                    "-1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode != 0
            assert "cannot be negative" in result.stderr.lower()

    def test_cli_write_negative_disc_total_error(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--disc-total",
                    "-1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode != 0
            assert "cannot be negative" in result.stderr.lower()

    def test_cli_write_negative_bpm_error(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--bpm",
                    "-1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode != 0
            assert "cannot be negative" in result.stderr.lower()

    def test_cli_write_negative_year_error(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--year",
                    "-1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode != 0
            assert "cannot be negative" in result.stderr.lower()
