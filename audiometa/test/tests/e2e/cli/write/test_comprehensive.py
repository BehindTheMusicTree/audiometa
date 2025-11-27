import subprocess
import sys

import pytest

from audiometa import get_unified_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.e2e
class TestCLIWriteComprehensive:
    def test_cli_write_all_fields_comprehensive(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "Comprehensive Test Title",
                    "--artist",
                    "Artist One",
                    "--artist",
                    "Artist Two",
                    "--album",
                    "Test Album",
                    "--album-artist",
                    "Album Artist",
                    "--year",
                    "2024",
                    "--genre",
                    "Rock",
                    "--genre",
                    "Blues",
                    "--track-number",
                    "5/12",
                    "--disc-number",
                    "1",
                    "--disc-total",
                    "2",
                    "--rating",
                    "85",
                    "--bpm",
                    "120",
                    "--language",
                    "eng",
                    "--composer",
                    "Composer One",
                    "--composer",
                    "Composer Two",
                    "--publisher",
                    "Test Publisher",
                    "--copyright",
                    "© 2024",
                    "--lyrics",
                    "Test lyrics",
                    "--comment",
                    "Test comment",
                    "--replaygain",
                    "+2.5 dB",
                    "--archival-location",
                    "Archive",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "Comprehensive Test Title"
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["Artist One", "Artist Two"]
            assert metadata.get(UnifiedMetadataKey.ALBUM) == "Test Album"
            assert metadata.get(UnifiedMetadataKey.ALBUM_ARTISTS) == ["Album Artist"]
            assert metadata.get(UnifiedMetadataKey.RELEASE_DATE) == "2024"
            assert metadata.get(UnifiedMetadataKey.GENRES_NAMES) == ["Rock", "Blues"]
            assert metadata.get(UnifiedMetadataKey.TRACK_NUMBER) == "5/12"
            assert metadata.get(UnifiedMetadataKey.DISC_NUMBER) == 1
            assert metadata.get(UnifiedMetadataKey.DISC_TOTAL) == 2
            assert metadata.get(UnifiedMetadataKey.RATING) == 85
            assert metadata.get(UnifiedMetadataKey.BPM) == 120
            assert metadata.get(UnifiedMetadataKey.LANGUAGE) == "eng"
            assert metadata.get(UnifiedMetadataKey.COMPOSERS) == ["Composer One", "Composer Two"]
            assert metadata.get(UnifiedMetadataKey.PUBLISHER) == "Test Publisher"
            assert metadata.get(UnifiedMetadataKey.COPYRIGHT) == "© 2024"
            assert metadata.get(UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS) == "Test lyrics"
            assert metadata.get(UnifiedMetadataKey.COMMENT) == "Test comment"
            assert metadata.get(UnifiedMetadataKey.REPLAYGAIN) == "+2.5 dB"
            # ARCHIVAL_LOCATION is not supported by ID3v2 format (MP3)
            # It's only supported by Vorbis (FLAC)

    def test_cli_write_flac_all_fields(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "FLAC Test",
                    "--artist",
                    "FLAC Artist",
                    "--album",
                    "FLAC Album",
                    "--track-number",
                    "3/10",
                    "--disc-number",
                    "1",
                    "--disc-total",
                    "2",
                    "--bpm",
                    "140",
                    "--language",
                    "eng",
                    "--composer",
                    "FLAC Composer",
                    "--publisher",
                    "FLAC Publisher",
                    "--copyright",
                    "© FLAC",
                    "--lyrics",
                    "FLAC lyrics",
                    "--comment",
                    "FLAC comment",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "FLAC Test"
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["FLAC Artist"]
            assert metadata.get(UnifiedMetadataKey.ALBUM) == "FLAC Album"
            assert metadata.get(UnifiedMetadataKey.TRACK_NUMBER) == "3/10"
            assert metadata.get(UnifiedMetadataKey.DISC_NUMBER) == 1
            assert metadata.get(UnifiedMetadataKey.DISC_TOTAL) == 2
            assert metadata.get(UnifiedMetadataKey.BPM) == 140
            assert metadata.get(UnifiedMetadataKey.LANGUAGE) == "eng"
            assert metadata.get(UnifiedMetadataKey.COMPOSERS) == ["FLAC Composer"]
            assert metadata.get(UnifiedMetadataKey.PUBLISHER) == "FLAC Publisher"
            assert metadata.get(UnifiedMetadataKey.COPYRIGHT) == "© FLAC"
            assert metadata.get(UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS) == "FLAC lyrics"
            assert metadata.get(UnifiedMetadataKey.COMMENT) == "FLAC comment"

    def test_cli_write_wav_all_fields(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "WAV Test",
                    "--artist",
                    "WAV Artist",
                    "--album",
                    "WAV Album",
                    "--year",
                    "2024",
                    "--genre",
                    "Rock",
                    "--rating",
                    "100",
                    "--bpm",
                    "120",
                    "--language",
                    "eng",
                    "--composer",
                    "WAV Composer",
                    "--copyright",
                    "© WAV",
                    "--comment",
                    "WAV comment",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "WAV Test"
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["WAV Artist"]
            assert metadata.get(UnifiedMetadataKey.ALBUM) == "WAV Album"
            assert metadata.get(UnifiedMetadataKey.RELEASE_DATE) == "2024"
            assert metadata.get(UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]
            assert metadata.get(UnifiedMetadataKey.RATING) == 100
            assert metadata.get(UnifiedMetadataKey.BPM) == 120
            assert metadata.get(UnifiedMetadataKey.LANGUAGE) == "eng"
            assert metadata.get(UnifiedMetadataKey.COMPOSERS) == ["WAV Composer"]
            assert metadata.get(UnifiedMetadataKey.COPYRIGHT) == "© WAV"
            assert metadata.get(UnifiedMetadataKey.COMMENT) == "WAV comment"
