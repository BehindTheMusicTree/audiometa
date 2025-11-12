import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestId3v2GenreReading:
    def test_id3v2_single_genre(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_genre(test_file, "Rock")

            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock"]

    def test_id3v2_multiple_genres_separate_frames(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_genres(test_file, ["Rock", "Alternative", "Indie"])

            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock", "Alternative", "Indie"]
