import pytest

from audiometa import get_unified_metadata, get_unified_metadata_field
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat

@pytest.mark.integration
class TestVorbisGenreReading:

    def test_vorbis_single_genre(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_genre(test_file.path, "Rock")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Rock"]

    def test_vorbis_multiple_genres_separate_entries(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_genre(test_file.path, "Rock; Alternative; Indie")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Rock", "Alternative", "Indie"]

    def test_vorbis_genre_with_double_backslash_separator(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_genre(test_file.path, "Rock\\\\Alternative\\\\Indie")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Rock", "Alternative", "Indie"]

    def test_vorbis_genre_custom_genre_names(self):
        custom_genres = [
            "Post-Rock", "Shoegaze", "Dream Pop", "Chillwave", "Vaporwave",
            "Synthwave", "Retrowave", "Outrun", "Future Funk", "Lo-Fi Hip Hop",
            "Ambient", "Drone", "Noise", "Experimental", "Avant-garde"
        ]
        
        for genre in custom_genres:
            with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
                VorbisMetadataSetter.set_genre(test_file.path, genre)
                
                metadata = get_unified_metadata(test_file.path)
                genres = metadata.get(UnifiedMetadataKey.GENRES_NAMES)
                
                assert genres == [genre]