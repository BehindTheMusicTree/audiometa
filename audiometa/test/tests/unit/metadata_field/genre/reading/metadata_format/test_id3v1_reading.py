import pytest
import subprocess
from pathlib import Path

from audiometa import get_unified_metadata, get_unified_metadata_field
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter


@pytest.mark.integration
class TestId3v1GenreReading:

    def test_id3v1_genre_code_17_rock(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_genre(test_file.path, "17")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Rock"]

    def test_id3v1_genre_code_0_blues(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_genre(test_file.path, "0")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Blues"]

    def test_id3v1_genre_code_32_classical(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_genre(test_file.path, "32")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Classical"]

    def test_id3v1_genre_code_80_folk(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_genre(test_file.path, "80")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Folk"]

    def test_id3v1_genre_code_131_indie(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_genre(test_file.path, "131")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Indie"]

    def test_id3v1_genre_code_189_dubstep(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_genre(test_file.path, "189")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Dubstep"]

    def test_id3v1_genre_code_255_unknown(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_genre(test_file.path, "255")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres is None