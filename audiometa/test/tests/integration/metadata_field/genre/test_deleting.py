import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestGenreDeleting:
    def test_delete_genre_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_genre(test_file, "Rock")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]

            update_metadata(test_file, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES) is None

    def test_delete_genre_id3v1(self):
        with temp_file_with_metadata({}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_genre(test_file, "Rock")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]

            update_metadata(test_file, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES) is None

    def test_delete_genre_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_genres(test_file, ["Rock"])
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]

            update_metadata(test_file, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES) is None

    def test_delete_genre_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_genre(test_file, "Rock")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]

            update_metadata(test_file, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES) is None

    def test_delete_genre_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_genre(test_file, "Rock")
            ID3v2MetadataSetter.set_title(test_file, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file, "Test Artist")

            update_metadata(test_file, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.ID3V2)

            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_genre_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES) is None
