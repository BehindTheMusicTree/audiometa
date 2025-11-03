import subprocess
import sys
import pytest

from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.e2e
class TestCLIInputValidationErrors:

    def test_cli_invalid_rating_value_negative(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--rating", "-5"
            ], capture_output=True, text=True)

            # Should fail due to negative rating - CLI validates explicitly
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output
            assert "rating" in stderr_output

    def test_cli_rating_value_allowed_without_normalization(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            # Any integer rating value should be allowed when normalized_rating_max_value is not provided
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--rating", "150"
            ], capture_output=True, text=True)

            # Should succeed - no write profile validation when normalized_rating_max_value is None
            assert result.returncode == 0

    def test_cli_rating_value_non_multiple_of_10_allowed(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--rating", "37"
            ], capture_output=True, text=True)

            # Should succeed - no write profile validation when normalized_rating_max_value is None
            assert result.returncode == 0

    def test_cli_invalid_rating_value_non_numeric(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--rating", "not-a-number"
            ], capture_output=True, text=True)

            # Should fail due to non-numeric rating
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "invalid" in stderr_output.lower() or "error" in stderr_output

    def test_cli_valid_rating_multiple_of_10(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--rating", "128"
            ], capture_output=True, text=True)

            # Should succeed - any integer rating value is allowed
            assert result.returncode == 0
            assert "updated metadata" in result.stdout.lower()

    def test_cli_invalid_year_value_non_numeric(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--year", "not-a-year"
            ], capture_output=True, text=True)

            # Should fail due to non-numeric year
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "invalid" in stderr_output.lower() or "error" in stderr_output

    def test_cli_invalid_year_value_negative(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--year", "-2023"
            ], capture_output=True, text=True)

            # Should fail due to invalid date format (negative year doesn't match YYYY format)
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output or "invalid" in stderr_output

    def test_cli_valid_year_value_future(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            future_year = str(2030 + 1)  # Future year is valid
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--year", future_year
            ], capture_output=True, text=True)

            # Should succeed - future years are allowed
            assert result.returncode == 0
            assert "updated metadata" in result.stdout.lower()

    def test_cli_write_no_metadata_fields(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path)
            ], capture_output=True, text=True)

            # Should fail due to no metadata fields
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "no metadata fields specified" in stderr_output

    def test_cli_write_empty_title_artist_album(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--title", "", "--artist", "", "--album", ""
            ], capture_output=True, text=True)

            # Should fail - empty strings are not considered valid metadata
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "no metadata fields specified" in stderr_output