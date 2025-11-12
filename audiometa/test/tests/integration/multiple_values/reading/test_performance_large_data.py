import time

import pytest

from audiometa import get_unified_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestPerformanceLargeData:
    def test_performance_with_many_entries(self):
        # Create temporary file with basic metadata
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            # Set many artists using temp_file_with_metadata
            artists_list = [f"Artist {i + 1}" for i in range(20)]
            VorbisMetadataSetter.set_artists(test_file, artists_list)

            for _ in range(5):
                unified_metadata = get_unified_metadata(test_file)
                artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)

                assert isinstance(artists, list)
                assert len(artists) == 20

    def test_performance_with_large_separated_values(self):
        # Create temporary file with basic metadata
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            # Set many artists using temp_file_with_metadata
            artists_list = [f"Artist {i + 1}" for i in range(50)]
            VorbisMetadataSetter.set_artists(test_file, artists_list)

            start_time = time.time()
            unified_metadata = get_unified_metadata(test_file)
            end_time = time.time()

            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)

            assert isinstance(artists, list)
            assert len(artists) == 50

            # Performance should be reasonable (less than 1 second for 50 artists)
            assert (end_time - start_time) < 1.0

    def test_performance_with_mixed_separators_large(self):
        # Create temporary file with basic metadata
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            # Test performance with complex separator scenarios
            complex_artists = [
                "Artist 1",
                "Artist 2",
                "Artist 3",
                "Artist 4",
                "Artist 5",
                "Artist 6",
                "Artist 7",
                "Artist 8",
                "Artist 9",
                "Artist 10",
                "Artist 11",
                "Artist 12",
                "Artist 13",
                "Artist 14",
                "Artist 15",
                "Artist 16",
                "Artist 17",
                "Artist 18",
                "Artist 19",
                "Artist 20",
                "Artist 21",
                "Artist 22",
                "Artist 23",
                "Artist 24",
                "Artist 25",
                "Artist 26",
                "Artist 27",
                "Artist 28",
                "Artist 29",
                "Artist 30",
            ]

            try:
                VorbisMetadataSetter.set_artists(test_file, complex_artists)
            except RuntimeError:
                pytest.skip("metaflac not available or failed to set complex separated artists")

            start_time = time.time()
            unified_metadata = get_unified_metadata(test_file)
            end_time = time.time()

            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)

            assert isinstance(artists, list)
            # Should have many artists after complex separation
            assert len(artists) >= 30

            # Performance should be reasonable
            assert (end_time - start_time) < 2.0

    def test_memory_usage_with_large_values(self):
        # Create temporary file with basic metadata
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            # Test with very long individual values
            long_artist = "A" * 50000  # 50,000 character artist name

            try:
                VorbisMetadataSetter.set_artist(test_file, long_artist)
            except RuntimeError:
                pytest.skip("metaflac not available or failed to set very long artist")

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)

            assert isinstance(artists, list)
            assert len(artists) == 1
            assert artists[0] == long_artist

    def test_performance_repeated_reads(self):
        # Create temporary file with basic metadata
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            # Set up test data
            try:
                artists_list = [f"Artist {i + 1}" for i in range(10)]
                VorbisMetadataSetter.set_artists(test_file, artists_list)
            except RuntimeError:
                pytest.skip("metaflac not available or failed to set test artists")

            # Test repeated reads
            start_time = time.time()
            for _ in range(100):
                unified_metadata = get_unified_metadata(test_file)
                artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
                assert isinstance(artists, list)
                assert len(artists) == 10
            end_time = time.time()

            # 100 reads should complete in reasonable time
            assert (end_time - start_time) < 5.0

    def test_performance_with_all_multi_value_fields(self):
        # Create temporary file with basic metadata
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            # Test performance when multiple multi-value fields are populated
            try:
                # Set multiple artists
                artists_list = [f"Artist {i + 1}" for i in range(10)]
                VorbisMetadataSetter.set_artists(test_file, artists_list)

                # Set multiple genres
                genres_list = [f"Genre {i + 1}" for i in range(5)]
                VorbisMetadataSetter.set_genres(test_file, genres_list)

                # Set multiple composers
                composers_list = [f"Composer {i + 1}" for i in range(8)]
                VorbisMetadataSetter.set_composers(test_file, composers_list)

            except RuntimeError:
                pytest.skip("metaflac not available or failed to set multiple multi-value fields")

            start_time = time.time()
            unified_metadata = get_unified_metadata(test_file)
            end_time = time.time()

            # Check all multi-value fields
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            assert isinstance(artists, list)
            assert len(artists) == 10

            genres = unified_metadata.get(UnifiedMetadataKey.GENRES_NAMES)
            assert isinstance(genres, list)
            assert len(genres) == 5

            composers = unified_metadata.get(UnifiedMetadataKey.COMPOSERS)
            assert isinstance(composers, list)
            assert len(composers) == 8

            # Performance should be reasonable
            assert (end_time - start_time) < 2.0

    def test_performance_with_whitespace_heavy_data(self):
        # Create temporary file with basic metadata
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            # Test performance with data that has lots of whitespace processing
            whitespace_heavy_artists = ["   Artist One   ", "   Artist Two   ", "   Artist Three   "]

            try:
                VorbisMetadataSetter.set_artists(test_file, whitespace_heavy_artists)
            except RuntimeError:
                pytest.skip("metaflac not available or failed to set whitespace-heavy artists")

            start_time = time.time()
            unified_metadata = get_unified_metadata(test_file)
            end_time = time.time()

            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist One" in artists
            assert "Artist Two" in artists
            assert "Artist Three" in artists

            # Check that whitespace was properly stripped
            for artist in artists:
                assert artist == artist.strip()

            # Performance should be reasonable
            assert (end_time - start_time) < 1.0
