import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIInputValidationErrors:
    def test_cli_invalid_rating_value_negative(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(temp_file_path), "--rating", "-5"],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should fail due to negative rating - CLI validates explicitly
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output
            assert "rating" in stderr_output

    def test_cli_rating_value_allowed_without_normalization(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            # Any integer rating value should be allowed when normalized_rating_max_value is not provided
            # Using a valid ID3v2 profile value (196 = 4 stars in BASE_255_NON_PROPORTIONAL profile)
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(temp_file_path), "--rating", "196"],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should succeed - no write profile validation when normalized_rating_max_value is None
            assert result.returncode == 0

    def test_cli_rating_whole_number_float_allowed(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            # Whole-number floats like 196.0 should be accepted and converted to integers
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(temp_file_path), "--rating", "196.0"],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should succeed - whole-number floats are converted to integers in raw mode
            assert result.returncode == 0

    def test_cli_rating_value_non_multiple_of_10_allowed(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(temp_file_path), "--rating", "37"],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should succeed - no write profile validation when normalized_rating_max_value is None
            assert result.returncode == 0

    def test_cli_invalid_rating_value_non_numeric(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(temp_file_path), "--rating", "not-a-number"],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should fail due to non-numeric rating
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "invalid" in stderr_output.lower() or "error" in stderr_output

    def test_cli_valid_rating_multiple_of_10(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(temp_file_path), "--rating", "128"],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should succeed - any integer rating value is allowed
            assert result.returncode == 0
            assert "updated metadata" in result.stdout.lower()

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

    def test_cli_write_no_metadata_fields(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "write", str(temp_file_path)],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should fail due to no metadata fields
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "no metadata fields specified" in stderr_output

    def test_cli_write_empty_title_artist_album(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(temp_file_path),
                    "--title",
                    "",
                    "--artist",
                    "",
                    "--album",
                    "",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should fail - empty strings are not considered valid metadata
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "no metadata fields specified" in stderr_output
