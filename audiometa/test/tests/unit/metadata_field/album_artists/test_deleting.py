import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter


@pytest.mark.integration
class TestAlbumArtistsDeleting:
    def test_delete_album_artists_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            # Set metadata using max metadata method (includes album artists)
            ID3v2MetadataSetter.set_max_metadata(test_file.path)
            # Verify album artists are set
            album_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS)
            assert album_artists is not None
        
            # Delete metadata by setting to None
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS) is None

    def test_delete_album_artists_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            # Set album artists using the unified API
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM_ARTISTS: ["Test Album Artist"]}, metadata_format=MetadataFormat.RIFF)
            # Verify album artists are set
            album_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS, metadata_format=MetadataFormat.RIFF)
            assert album_artists == ["Test Album Artist"]
        
            # Delete metadata by setting to None
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS) is None

    def test_delete_album_artists_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            # Set metadata using max metadata method (includes album artists)
            VorbisMetadataSetter.set_max_metadata(test_file.path)
            # Verify album artists are set
            album_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS)
            assert album_artists is not None
        
            # Delete metadata by setting to None
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS) is None

    def test_delete_album_artists_preserves_other_fields(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            # Set metadata using max metadata method (includes album artists and other fields)
            ID3v2MetadataSetter.set_max_metadata(test_file.path)
            # Verify album artists are set
            album_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS)
            assert album_artists is not None
        
            # Delete only album artists
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
        
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS) is None
            # Verify other fields are preserved
            title = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TITLE)
            assert title is not None

    def test_delete_album_artists_already_none(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            # Try to delete album artists that don't exist
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS) is None

    def test_delete_album_artists_empty_list(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            # Set metadata using max metadata method (includes album artists)
            ID3v2MetadataSetter.set_max_metadata(test_file.path)
            # Delete the album artists
            update_metadata(test_file.path, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS) is None
