import subprocess
import sys

import pytest

from audiometa import get_unified_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.e2e
class TestCLIWriteListFields:
    def test_cli_write_multiple_artists(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--artist",
                    "Artist One",
                    "--artist",
                    "Artist Two",
                    "--artist",
                    "Artist Three",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["Artist One", "Artist Two", "Artist Three"]

    def test_cli_write_multiple_album_artists(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--album-artist",
                    "Album Artist One",
                    "--album-artist",
                    "Album Artist Two",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ALBUM_ARTISTS) == ["Album Artist One", "Album Artist Two"]

    def test_cli_write_multiple_genres(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--genre",
                    "Rock",
                    "--genre",
                    "Blues",
                    "--genre",
                    "Jazz",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.GENRES_NAMES) == ["Rock", "Blues", "Jazz"]

    def test_cli_write_multiple_composers(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--composer",
                    "Composer One",
                    "--composer",
                    "Composer Two",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.COMPOSERS) == ["Composer One", "Composer Two"]
