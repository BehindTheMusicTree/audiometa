import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.riff import RIFFMetadataSetter


@pytest.mark.integration
class TestRiffGenreParsing:

    def test_riff_genre_codes_only_semicolon(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_genre_text(test_file.path, "17; 20; 131")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Rock", "Alternative", "Indie"]

    def test_riff_genre_mixed_codes_and_names(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_genre_text(test_file.path, "Rock; 20; Indie")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Rock", "Alternative", "Indie"]

    def test_riff_genre_single_code(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_genre_text(test_file.path, "17")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Rock"]

    def test_riff_genre_single_name(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_genre_text(test_file.path, "Rock")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == ["Rock"]

    def test_riff_genre_unknown_code(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_genre_text(test_file.path, "999")
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres is None

    def test_riff_genre_very_long_text(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            long_genre = "Very Long Genre Name That Might Exceed Normal Limits And Test Edge Cases"
            RIFFMetadataSetter.set_genre_text(test_file.path, long_genre)
            
            genres = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES)
            
            assert genres == [long_genre]