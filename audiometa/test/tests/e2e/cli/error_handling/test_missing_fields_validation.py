import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIMissingFieldsValidation:
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
