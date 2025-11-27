import subprocess
import sys

import pytest

from audiometa import get_unified_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.e2e
class TestCLIWriteStringFields:
    def test_cli_write_all_string_fields(self):
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
                    "--language",
                    "eng",
                    "--publisher",
                    "Test Publisher",
                    "--copyright",
                    "© 2024 Test",
                    "--lyrics",
                    "Test lyrics text",
                    "--comment",
                    "Test comment",
                    "--replaygain",
                    "+2.5 dB",
                    "--archival-location",
                    "Archive Location",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "Test Title"
            assert metadata.get(UnifiedMetadataKey.LANGUAGE) == "eng"
            assert metadata.get(UnifiedMetadataKey.PUBLISHER) == "Test Publisher"
            assert metadata.get(UnifiedMetadataKey.COPYRIGHT) == "© 2024 Test"
            assert metadata.get(UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS) == "Test lyrics text"
            assert metadata.get(UnifiedMetadataKey.COMMENT) == "Test comment"
            assert metadata.get(UnifiedMetadataKey.REPLAYGAIN) == "+2.5 dB"
            # ARCHIVAL_LOCATION is not supported by ID3v2 format (MP3)
            # It's only supported by Vorbis (FLAC)
