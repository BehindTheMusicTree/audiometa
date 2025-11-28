import subprocess
import sys

import pytest

from audiometa import get_unified_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.e2e
class TestCLIWriteIntegerFields:
    def test_cli_write_integer_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--disc-number",
                    "2",
                    "--disc-total",
                    "3",
                    "--bpm",
                    "120",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.DISC_NUMBER) == 2
            assert metadata.get(UnifiedMetadataKey.DISC_TOTAL) == 3
            assert metadata.get(UnifiedMetadataKey.BPM) == 120

    def test_cli_write_track_number_simple(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--track-number",
                    "5",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TRACK_NUMBER) == "5"

    def test_cli_write_track_number_with_total(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--track-number",
                    "5/12",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TRACK_NUMBER) == "5/12"

    def test_cli_write_release_date_year(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--year",
                    "2024",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.RELEASE_DATE) == "2024"

    def test_cli_write_release_date_full(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--release-date",
                    "2024-01-15",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.RELEASE_DATE) == "2024-01-15"

    def test_cli_write_year_takes_precedence_over_release_date(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--year",
                    "2023",
                    "--release-date",
                    "2024-01-15",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.RELEASE_DATE) == "2023"
