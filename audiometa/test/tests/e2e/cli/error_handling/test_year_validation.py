import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIYearValidation:
    def test_cli_invalid_year_value_non_numeric(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(temp_file_path), "--year", "not-a-year"],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should fail due to non-numeric year
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "invalid" in stderr_output.lower() or "error" in stderr_output

    def test_cli_invalid_year_value_negative(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(temp_file_path), "--year", "-2023"],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should fail due to invalid date format (negative year doesn't match YYYY format)
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output or "invalid" in stderr_output

    def test_cli_valid_year_value_future(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            future_year = str(2030 + 1)  # Future year is valid
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(temp_file_path), "--year", future_year],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should succeed - future years are allowed
            assert result.returncode == 0
            assert "updated metadata" in result.stdout.lower()
