import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.exceptions import InvalidMetadataFieldTypeError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestAlbumArtistsWriting:
    def test_id3v2(self):
        test_album_artists = ["Album Artist 1", "Album Artist 2"]
        test_metadata = {UnifiedMetadataKey.ALBUM_ARTISTS: test_album_artists}
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ALBUM_ARTISTS) == test_album_artists

    def test_riff(self):
        test_album_artists = ["RIFF Album Artist 1", "RIFF Album Artist 2"]
        test_metadata = {UnifiedMetadataKey.ALBUM_ARTISTS: test_album_artists}
        with temp_file_with_metadata({}, "wav") as test_file:
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.RIFF)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ALBUM_ARTISTS) == test_album_artists

    def test_vorbis(self):
        test_album_artists = ["Vorbis Album Artist 1", "Vorbis Album Artist 2"]
        test_metadata = {UnifiedMetadataKey.ALBUM_ARTISTS: test_album_artists}
        with temp_file_with_metadata({}, "flac") as test_file:
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.VORBIS)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ALBUM_ARTISTS) == test_album_artists

    def test_id3v1(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError

        test_album_artists = ["ID3v1 Album Artist"]
        test_metadata = {UnifiedMetadataKey.ALBUM_ARTISTS: test_album_artists}
        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.ALBUM_ARTISTS metadata not supported by ID3v1 format",
            ),
        ):
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V1)

    def test_invalid_type_raises(self):
        with temp_file_with_metadata({}, "mp3") as test_file, pytest.raises(InvalidMetadataFieldTypeError):
            update_metadata(test_file, {UnifiedMetadataKey.ALBUM_ARTISTS: "Single Album Artist"})
