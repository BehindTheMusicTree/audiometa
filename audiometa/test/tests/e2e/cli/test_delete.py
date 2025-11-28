import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIDelete:
    def test_cli_delete_metadata(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "delete", str(test_file)],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Deleted metadata" in result.stdout or "No metadata found" in result.stderr
