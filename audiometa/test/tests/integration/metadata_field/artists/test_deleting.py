import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.vorbis import VorbisMetadataSetter


@pytest.mark.integration
class TestArtistsDeleting:
    def test_delete_artists_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_artists(test_file.path, "Artist 1; Artist 2")
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) == ["Artist 1", "Artist 2"]
        
            # Delete metadata using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) is None

    def test_delete_artists_id3v1(self):
        with TempFileWithMetadata({}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_artist(test_file.path, "Artist 1")
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) == ["Artist 1"]
        
            # Delete metadata using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) is None

    def test_delete_artists_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_artist(test_file.path, "Artist 1")
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) == ["Artist 1"]
        
            # Delete metadata using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) is None

    def test_delete_artists_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file.path, ["Artist 1", "Artist 2"])
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) == ["Artist 1", "Artist 2"]
        
            # Delete metadata using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) is None

    def test_delete_artists_preserves_other_fields(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_artists(test_file.path, "Test Artist")
            ID3v2MetadataSetter.set_title(test_file.path, "Test Title")
            ID3v2MetadataSetter.set_album(test_file.path, "Test Album")
        
            # Delete only artists using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
        
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) is None
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM) == "Test Album"

    def test_delete_artists_already_none(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            # Try to delete artists that don't exist
            update_metadata(test_file.path, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) is None

    def test_delete_artists_empty_list(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_artists(test_file.path, "")
            # Delete the empty artists using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) is None
