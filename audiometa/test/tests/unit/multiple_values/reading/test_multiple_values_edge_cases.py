import pytest

from audiometa import get_unified_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter


class TestMultipleValuesEdgeCases:
    def test_numeric_entries(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file.path, ["Artist 1", "Artist 2", "123"])
            
            unified_metadata = get_unified_metadata(test_file.path)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            
            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist 1" in artists
            assert "Artist 2" in artists
            assert "123" in artists

    def test_case_sensitivity_preservation(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file.path, [
                "Artist One",
                "ARTIST TWO", 
                "artist three",
                "ArTiSt FoUr"
            ])
            
            unified_metadata = get_unified_metadata(test_file.path)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            
            assert isinstance(artists, list)
            assert len(artists) == 4
            assert "Artist One" in artists
            assert "ARTIST TWO" in artists
            assert "artist three" in artists
            assert "ArTiSt FoUr" in artists

    def test_duplicate_entries_preservation(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file.path, [
                "Artist One",
                "Artist Two", 
                "Artist One",  # Duplicate
                "Artist Three",
                "Artist Two"   # Another duplicate
            ])
            
            unified_metadata = get_unified_metadata(test_file.path)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            
            assert isinstance(artists, list)
            assert len(artists) == 5  # Including duplicates
            assert artists.count("Artist One") == 2
            assert artists.count("Artist Two") == 2
            assert artists.count("Artist Three") == 1

    def test_order_preservation(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file.path, [
                "First Artist",
                "Second Artist",
                "Third Artist",
                "Fourth Artist"
            ])
            
            unified_metadata = get_unified_metadata(test_file.path)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            
            assert isinstance(artists, list)
            assert len(artists) == 4
            assert artists[0] == "First Artist"
            assert artists[1] == "Second Artist"
            assert artists[2] == "Third Artist"
            assert artists[3] == "Fourth Artist"

    def test_very_long_single_entry(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            long_artist = "A" * 10000  # 10,000 character artist name
            VorbisMetadataSetter.set_artists(test_file.path, [long_artist])
            
            unified_metadata = get_unified_metadata(test_file.path)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            
            assert isinstance(artists, list)
            assert len(artists) == 1
            assert artists[0] == long_artist

    def test_mixed_metadata_types(self):
        with TempFileWithMetadata({"title": "Single Title"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file.path, ["Artist One", "Artist Two"])
            VorbisMetadataSetter.set_genres(test_file.path, ["Rock", "Alternative"])
            
            unified_metadata = get_unified_metadata(test_file.path)
            
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            assert isinstance(artists, list)
            assert len(artists) == 2
            assert "Artist One" in artists
            assert "Artist Two" in artists
            
            genres = unified_metadata.get(UnifiedMetadataKey.GENRES_NAMES)
            assert isinstance(genres, list)
            assert len(genres) == 2
            assert "Rock" in genres
            assert "Alternative" in genres
            
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)
            assert isinstance(title, str)
            assert title == "Single Title"

    def test_corrupted_multiple_entries(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            unified_metadata = get_unified_metadata(test_file.path)
            
            assert isinstance(unified_metadata, dict)
            
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            if artists is not None:
                assert isinstance(artists, list)
