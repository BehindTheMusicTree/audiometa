import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.integration
class TestId3v1GenreReading:
    def test_id3v1_genre_code_17_rock(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file_path:
            ID3v1MetadataSetter.set_genre(test_file_path, "17")

            genres = get_unified_metadata_field(test_file_path, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock"]

    def test_id3v1_genre_code_0_blues(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file_path:
            ID3v1MetadataSetter.set_genre(test_file_path, "0")

            genres = get_unified_metadata_field(test_file_path, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Blues"]

    def test_id3v1_genre_code_32_classical(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file_path:
            ID3v1MetadataSetter.set_genre(test_file_path, "32")

            genres = get_unified_metadata_field(test_file_path, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Classical"]

    def test_id3v1_genre_code_80_folk(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file_path:
            ID3v1MetadataSetter.set_genre(test_file_path, "80")

            genres = get_unified_metadata_field(test_file_path, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Folk"]

    def test_id3v1_genre_code_131_indie(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file_path:
            ID3v1MetadataSetter.set_genre(test_file_path, "131")

            genres = get_unified_metadata_field(test_file_path, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Indie"]

    def test_id3v1_genre_code_189_dubstep(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file_path:
            ID3v1MetadataSetter.set_genre(test_file_path, "189")

            genres = get_unified_metadata_field(test_file_path, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Dubstep"]

    def test_id3v1_genre_code_255_unknown(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file_path:
            ID3v1MetadataSetter.set_genre(test_file_path, "255")

            genres = get_unified_metadata_field(test_file_path, UnifiedMetadataKey.GENRES_NAMES)

            assert genres is None
