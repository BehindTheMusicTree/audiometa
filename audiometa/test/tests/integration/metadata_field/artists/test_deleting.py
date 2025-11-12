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
class TestArtistsDeleting:
    def test_delete_artists_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_artists(test_file, "Artist 1; Artist 2")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Artist 1", "Artist 2"]

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) is None

    def test_delete_artists_id3v1(self):
        with temp_file_with_metadata({}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_artist(test_file, "Artist 1")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Artist 1"]

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) is None

    def test_delete_artists_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_artist(test_file, "Artist 1")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Artist 1"]

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) is None

    def test_delete_artists_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist 1", "Artist 2"])
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Artist 1", "Artist 2"]

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) is None

    def test_delete_artists_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_artists(test_file, "Test Artist")
            ID3v2MetadataSetter.set_title(test_file, "Test Title")
            ID3v2MetadataSetter.set_album(test_file, "Test Album")

            # Delete only artists using library API
            update_metadata(test_file, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)

            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM) == "Test Album"

    def test_delete_artists_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Try to delete artists that don't exist
            update_metadata(test_file, {UnifiedMetadataKey.ARTISTS: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) is None
