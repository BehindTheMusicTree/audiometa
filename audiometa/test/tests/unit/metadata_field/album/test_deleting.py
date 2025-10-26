import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.vorbis import VorbisMetadataSetter


@pytest.mark.integration
class TestAlbumDeleting:
    def test_delete_album_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_album(test_file.path, "Test Album")
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) == "Test Album"
            
            # Delete metadata using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) is None

    def test_delete_album_id3v1(self):
        with TempFileWithMetadata({}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_album(test_file.path, "Test Album")
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) == "Test Album"
            
            # Delete metadata using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) is None

    def test_delete_album_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_album(test_file.path, "Test Album")
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) == "Test Album"
            
            # Delete metadata using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) is None

    def test_delete_album_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_album(test_file.path, "Test Album")
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) == "Test Album"
            
            # Delete metadata using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) is None

    def test_delete_album_preserves_other_fields(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_album(test_file.path, "Test Album")
            ID3v2MetadataSetter.set_title(test_file.path, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file.path, "Test Artist")
            
            # Delete only album using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM: None}, metadata_format=MetadataFormat.ID3V2)
            
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) is None
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_album_already_none(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            # Try to delete album that doesn't exist
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) is None

    def test_delete_album_empty_string(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_album(test_file.path, "")
            # Delete the empty album using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) is None
