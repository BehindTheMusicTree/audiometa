import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestAlbumArtistsDeleting:
    def test_delete_album_artists_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Set metadata using max metadata method (includes album artists)
            ID3v2MetadataSetter.set_max_metadata(test_file)
            # Verify album artists are set
            album_artists = get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM_ARTISTS)
            assert album_artists is not None

            # Delete metadata by setting to None
            update_metadata(test_file, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM_ARTISTS) is None

    def test_delete_album_artists_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            # Set album artists using the unified API
            update_metadata(
                test_file,
                {UnifiedMetadataKey.ALBUM_ARTISTS: ["Test Album Artist"]},
                metadata_format=MetadataFormat.RIFF,
            )
            # Verify album artists are set
            album_artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ALBUM_ARTISTS, metadata_format=MetadataFormat.RIFF
            )
            assert album_artists == ["Test Album Artist"]

            # Delete metadata by setting to None
            update_metadata(test_file, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM_ARTISTS) is None

    def test_delete_album_artists_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            # Set metadata using max metadata method (includes album artists)
            VorbisMetadataSetter.set_max_metadata(test_file)
            # Verify album artists are set
            album_artists = get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM_ARTISTS)
            assert album_artists is not None

            # Delete metadata by setting to None
            update_metadata(test_file, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM_ARTISTS) is None

    def test_delete_album_artists_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Set metadata using max metadata method (includes album artists and other fields)
            ID3v2MetadataSetter.set_max_metadata(test_file)
            # Verify album artists are set
            album_artists = get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM_ARTISTS)
            assert album_artists is not None

            # Delete only album artists
            update_metadata(test_file, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)

            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM_ARTISTS) is None
            # Verify other fields are preserved
            title = get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE)
            assert title is not None

    def test_delete_album_artists_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Try to delete album artists that don't exist
            update_metadata(test_file, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM_ARTISTS) is None

    def test_delete_album_artists_with_existing_metadata(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Set metadata using max metadata method (includes album artists)
            ID3v2MetadataSetter.set_max_metadata(test_file)
            # Delete the album artists
            update_metadata(test_file, {UnifiedMetadataKey.ALBUM_ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM_ARTISTS) is None
