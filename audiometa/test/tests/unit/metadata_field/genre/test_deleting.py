import pytest

from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.vorbis import VorbisMetadataSetter


@pytest.mark.integration
class TestGenreDeleting:
    def test_delete_genre_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_genre(test_file.path, "Rock")
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]
        
            update_metadata(test_file.path, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) is None

    def test_delete_genre_id3v1(self):
        with TempFileWithMetadata({}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_genre(test_file.path, "Rock")
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]
        
            update_metadata(test_file.path, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) is None

    def test_delete_genre_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_genres(test_file.path, ["Rock"])
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]
        
            update_metadata(test_file.path, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) is None

    def test_delete_genre_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_genre(test_file.path, "Rock")
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]
        
            update_metadata(test_file.path, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) is None

    def test_delete_genre_preserves_other_fields(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_genre(test_file.path, "Rock")
            ID3v2MetadataSetter.set_title(test_file.path, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file.path, "Test Artist")
        
            update_metadata(test_file.path, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.ID3V2)
        
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) is None
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_genre_already_none(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            update_metadata(test_file.path, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) is None

    def test_delete_genre_empty_string(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_genre(test_file.path, "")
            update_metadata(test_file.path, {UnifiedMetadataKey.GENRES_NAMES: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.GENRES_NAMES) is None
