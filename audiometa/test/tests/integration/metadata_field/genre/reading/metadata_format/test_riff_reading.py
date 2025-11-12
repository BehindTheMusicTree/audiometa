import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestRiffGenreParsing:
    def test_riff_genre_codes_only_semicolon(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_genre_text(test_file, "17; 20; 131")

            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock", "Alternative", "Indie"]

    def test_riff_genre_mixed_codes_and_names(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_genre_text(test_file, "Rock; 20; Indie")

            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock", "Alternative", "Indie"]

    def test_riff_genre_single_code(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_genre_text(test_file, "17")

            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock"]

    def test_riff_genre_single_name(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_genre_text(test_file, "Rock")

            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock"]

    def test_riff_genre_unknown_code(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_genre_text(test_file, "999")

            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres is None

    def test_riff_genre_very_long_text(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            long_genre = "Very Long Genre Name That Might Exceed Normal Limits And Test Edge Cases"
            RIFFMetadataSetter.set_genre_text(test_file, long_genre)

            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == [long_genre]
