import json
import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIReadMetadataContent:
    def test_cli_read_all_metadata_fields_mp3(self):
        with temp_file_with_metadata(
            {
                "title": "Test Title",
                "artist": "Test Artist",
                "album": "Test Album",
                "album_artist": "Test Album Artist",
                "genre": "Rock",
                "year": "2024",
                "track": "5/12",
                "disc_number": 1,
                "disc_total": 2,
                "rating": 85,
                "bpm": 120,
                "language": "eng",
                "composer": "Test Composer",
                "publisher": "Test Publisher",
                "copyright": "© 2024",
                "comment": "Test comment",
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
            assert unified.get("title") == "Test Title"
            assert unified.get("artists") == ["Test Artist"]
            assert unified.get("album") == "Test Album"
            assert unified.get("album_artists") == ["Test Album Artist"]
            assert unified.get("genres_names") == ["Rock"]
            assert unified.get("release_date") == "2024"
            assert unified.get("track_number") == "5/12"
            assert unified.get("disc_number") == 1
            assert unified.get("disc_total") == 2
            assert unified.get("rating") == 85
            assert unified.get("bpm") == 120
            assert unified.get("language") == "eng"
            assert unified.get("composer") == ["Test Composer"]
            assert unified.get("publisher") == "Test Publisher"
            assert unified.get("copyright") == "© 2024"
            assert unified.get("comment") == "Test comment"

    def test_cli_read_all_metadata_fields_flac(self):
        with temp_file_with_metadata(
            {
                "title": "FLAC Title",
                "artist": "FLAC Artist",
                "album": "FLAC Album",
                "track_number": "3/10",
                "disc_number": 1,
                "disc_total": 2,
                "bpm": 140,
                "language": "eng",
                "composer": "FLAC Composer",
                "publisher": "FLAC Publisher",
                "copyright": "© FLAC",
                "lyrics": "FLAC lyrics",
                "comment": "FLAC comment",
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
            assert unified.get("title") == "FLAC Title"
            assert unified.get("artists") == ["FLAC Artist"]
            assert unified.get("album") == "FLAC Album"
            assert unified.get("track_number") == "3/10"
            assert unified.get("disc_number") == 1
            assert unified.get("disc_total") == 2
            assert unified.get("bpm") == 140
            assert unified.get("language") == "eng"
            assert unified.get("composer") == ["FLAC Composer"]
            assert unified.get("publisher") == "FLAC Publisher"
            assert unified.get("copyright") == "© FLAC"
            assert unified.get("unsynchronized_lyrics") == "FLAC lyrics"
            assert unified.get("comment") == "FLAC comment"

    def test_cli_read_all_metadata_fields_wav(self):
        with temp_file_with_metadata(
            {
                "title": "WAV Title",
                "artist": "WAV Artist",
                "album": "WAV Album",
                "year": "2024",
                "genre": "Rock",
                "rating": 100,
                "bpm": 120,
                "language": "eng",
                "composer": "WAV Composer",
                "copyright": "© WAV",
                "comment": "WAV comment",
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
            assert unified.get("title") == "WAV Title"
            assert unified.get("artists") == ["WAV Artist"]
            assert unified.get("album") == "WAV Album"
            assert unified.get("release_date") == "2024"
            assert unified.get("genres_names") == ["Rock"]
            assert unified.get("rating") == 100
            assert unified.get("bpm") == 120
            assert unified.get("language") == "eng"
            assert unified.get("composer") == ["WAV Composer"]
            assert unified.get("copyright") == "© WAV"
            assert unified.get("comment") == "WAV comment"

    def test_cli_read_multiple_artists(self):
        with temp_file_with_metadata({"artist": ["Artist One", "Artist Two", "Artist Three"]}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            unified = data.get("unified_metadata", {})
            assert unified.get("artists") == ["Artist One", "Artist Two", "Artist Three"]

    def test_cli_read_multiple_genres(self):
        with temp_file_with_metadata({"genre": ["Rock", "Blues", "Jazz"]}, "mp3") as test_file:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            unified = data.get("unified_metadata", {})
            assert unified.get("genres_names") == ["Rock", "Blues", "Jazz"]
