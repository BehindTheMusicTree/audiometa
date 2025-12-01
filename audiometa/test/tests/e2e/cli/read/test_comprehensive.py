import json
import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.e2e
class TestCLIReadComprehensive:
    def test_cli_read_all_fields_comprehensive_mp3(self):
        with temp_file_with_metadata(
            {
                "title": "Comprehensive Test Title",
                "artist": ["Artist One", "Artist Two"],
                "album": "Test Album",
                "album_artist": ["Album Artist"],
                "year": "2024",
                "genre": ["Rock", "Blues"],
                "track": "5/12",
                "disc_number": 1,
                "disc_total": 2,
                "rating": 85,
                "bpm": 120,
                "language": "eng",
                "composer": ["Composer One", "Composer Two"],
                "publisher": "Test Publisher",
                "copyright": "© 2024",
                "lyrics": "Test lyrics",
                "comment": "Test comment",
                "isrc": "USRC17607839",
            },
            "mp3",
        ) as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            unified = data.get("unified_metadata", {})

            assert unified.get(UnifiedMetadataKey.TITLE) == "Comprehensive Test Title"
            assert unified.get(UnifiedMetadataKey.ARTISTS) == ["Artist One", "Artist Two"]
            assert unified.get(UnifiedMetadataKey.ALBUM) == "Test Album"
            assert unified.get(UnifiedMetadataKey.ALBUM_ARTISTS) == ["Album Artist"]
            assert unified.get(UnifiedMetadataKey.RELEASE_DATE) == "2024"
            assert unified.get(UnifiedMetadataKey.GENRES_NAMES) == ["Rock", "Blues"]
            assert unified.get(UnifiedMetadataKey.TRACK_NUMBER) == "5/12"
            assert unified.get(UnifiedMetadataKey.DISC_NUMBER) == 1
            assert unified.get(UnifiedMetadataKey.DISC_TOTAL) == 2
            assert unified.get(UnifiedMetadataKey.RATING) == 85
            assert unified.get(UnifiedMetadataKey.BPM) == 120
            assert unified.get(UnifiedMetadataKey.LANGUAGE) == "eng"
            assert unified.get(UnifiedMetadataKey.COMPOSERS) == ["Composer One", "Composer Two"]
            assert unified.get(UnifiedMetadataKey.PUBLISHER) == "Test Publisher"
            assert unified.get(UnifiedMetadataKey.COPYRIGHT) == "© 2024"
            assert unified.get(UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS) == "Test lyrics"
            assert unified.get(UnifiedMetadataKey.COMMENT) == "Test comment"
            assert unified.get(UnifiedMetadataKey.ISRC) == "USRC17607839"
            # REPLAYGAIN and ARCHIVAL_LOCATION are not supported by ID3v2 format (MP3)

    def test_cli_read_all_fields_comprehensive_flac(self):
        with temp_file_with_metadata(
            {
                "title": "FLAC Comprehensive Test",
                "artist": ["FLAC Artist"],
                "album": "FLAC Album",
                "track_number": "3/10",
                "disc_number": 1,
                "disc_total": 2,
                "bpm": 140,
                "language": "eng",
                "composer": ["FLAC Composer"],
                "publisher": "FLAC Publisher",
                "copyright": "© FLAC",
                "lyrics": "FLAC lyrics",
                "comment": "FLAC comment",
                "replaygain": "+2.5 dB",
                "isrc": "FRXXX1800001",
            },
            "flac",
        ) as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            unified = data.get("unified_metadata", {})

            assert unified.get(UnifiedMetadataKey.TITLE) == "FLAC Comprehensive Test"
            assert unified.get(UnifiedMetadataKey.ARTISTS) == ["FLAC Artist"]
            assert unified.get(UnifiedMetadataKey.ALBUM) == "FLAC Album"
            assert unified.get(UnifiedMetadataKey.TRACK_NUMBER) == "3/10"
            assert unified.get(UnifiedMetadataKey.DISC_NUMBER) == 1
            assert unified.get(UnifiedMetadataKey.DISC_TOTAL) == 2
            assert unified.get(UnifiedMetadataKey.BPM) == 140
            assert unified.get(UnifiedMetadataKey.LANGUAGE) == "eng"
            assert unified.get(UnifiedMetadataKey.COMPOSERS) == ["FLAC Composer"]
            assert unified.get(UnifiedMetadataKey.PUBLISHER) == "FLAC Publisher"
            assert unified.get(UnifiedMetadataKey.COPYRIGHT) == "© FLAC"
            assert unified.get(UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS) == "FLAC lyrics"
            assert unified.get(UnifiedMetadataKey.COMMENT) == "FLAC comment"
            assert unified.get(UnifiedMetadataKey.REPLAYGAIN) == "+2.5 dB"
            assert unified.get(UnifiedMetadataKey.ISRC) == "FRXXX1800001"
            # ARCHIVAL_LOCATION is not supported by Vorbis format (FLAC)

    def test_cli_read_all_fields_comprehensive_wav(self):
        with temp_file_with_metadata(
            {
                "title": "WAV Comprehensive Test",
                "artist": ["WAV Artist"],
                "album": "WAV Album",
                "year": "2024",
                "genre": ["Rock"],
                "rating": 100,
                "bpm": 120,
                "language": "eng",
                "composer": ["WAV Composer"],
                "copyright": "© WAV",
                "comment": "WAV comment",
                "isrc": "GBUM71505078",
            },
            "wav",
        ) as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            unified = data.get("unified_metadata", {})

            assert unified.get(UnifiedMetadataKey.TITLE) == "WAV Comprehensive Test"
            assert unified.get(UnifiedMetadataKey.ARTISTS) == ["WAV Artist"]
            assert unified.get(UnifiedMetadataKey.ALBUM) == "WAV Album"
            assert unified.get(UnifiedMetadataKey.RELEASE_DATE) == "2024"
            assert unified.get(UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]
            assert unified.get(UnifiedMetadataKey.RATING) == 100
            assert unified.get(UnifiedMetadataKey.BPM) == 120
            assert unified.get(UnifiedMetadataKey.LANGUAGE) == "eng"
            assert unified.get(UnifiedMetadataKey.COMPOSERS) == ["WAV Composer"]
            assert unified.get(UnifiedMetadataKey.COPYRIGHT) == "© WAV"
            assert unified.get(UnifiedMetadataKey.COMMENT) == "WAV comment"
            assert unified.get(UnifiedMetadataKey.ISRC) == "GBUM71505078"

    def test_cli_read_comprehensive_roundtrip(self):
        """Test that we can write all fields via CLI and read them back correctly."""
        with temp_file_with_metadata({}, "mp3") as test_file:
            write_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "Roundtrip Test",
                    "--artist",
                    "Roundtrip Artist One",
                    "--artist",
                    "Roundtrip Artist Two",
                    "--album",
                    "Roundtrip Album",
                    "--album-artist",
                    "Roundtrip Album Artist",
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
                    "Roundtrip Composer",
                    "--publisher",
                    "Roundtrip Publisher",
                    "--copyright",
                    "© Roundtrip",
                    "--lyrics",
                    "Roundtrip lyrics",
                    "--comment",
                    "Roundtrip comment",
                    "--isrc",
                    "USRC17607839",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert write_result.returncode == 0

            read_result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert read_result.returncode == 0
            data = json.loads(read_result.stdout)
            unified = data.get("unified_metadata", {})

            assert unified.get(UnifiedMetadataKey.TITLE) == "Roundtrip Test"
            assert unified.get(UnifiedMetadataKey.ARTISTS) == ["Roundtrip Artist One", "Roundtrip Artist Two"]
            assert unified.get(UnifiedMetadataKey.ALBUM) == "Roundtrip Album"
            assert unified.get(UnifiedMetadataKey.ALBUM_ARTISTS) == ["Roundtrip Album Artist"]
            assert unified.get(UnifiedMetadataKey.RELEASE_DATE) == "2024"
            assert unified.get(UnifiedMetadataKey.GENRES_NAMES) == ["Rock", "Blues"]
            assert unified.get(UnifiedMetadataKey.TRACK_NUMBER) == "5/12"
            assert unified.get(UnifiedMetadataKey.DISC_NUMBER) == 1
            assert unified.get(UnifiedMetadataKey.DISC_TOTAL) == 2
            assert unified.get(UnifiedMetadataKey.RATING) == 85
            assert unified.get(UnifiedMetadataKey.BPM) == 120
            assert unified.get(UnifiedMetadataKey.LANGUAGE) == "eng"
            assert unified.get(UnifiedMetadataKey.COMPOSERS) == ["Roundtrip Composer"]
            assert unified.get(UnifiedMetadataKey.PUBLISHER) == "Roundtrip Publisher"
            assert unified.get(UnifiedMetadataKey.COPYRIGHT) == "© Roundtrip"
            assert unified.get(UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS) == "Roundtrip lyrics"
            assert unified.get(UnifiedMetadataKey.COMMENT) == "Roundtrip comment"
            assert unified.get(UnifiedMetadataKey.ISRC) == "USRC17607839"
