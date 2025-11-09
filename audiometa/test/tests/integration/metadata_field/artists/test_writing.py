import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.exceptions import InvalidMetadataFieldTypeError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.integration
class TestArtistsWriting:
    def test_id3v2(self):
        test_artists = ["Test Artist 1", "Test Artist 2"]
        test_metadata = {UnifiedMetadataKey.ARTISTS: test_artists}
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            update_metadata(test_file_path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file_path)
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == test_artists

    def test_riff(self):
        test_artists = ["RIFF Artist 1", "RIFF Artist 2"]
        test_metadata = {UnifiedMetadataKey.ARTISTS: test_artists}
        with temp_file_with_metadata({}, "wav") as test_file_path:
            update_metadata(test_file_path, test_metadata, metadata_format=MetadataFormat.RIFF)
            metadata = get_unified_metadata(test_file_path)
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == test_artists

    def test_vorbis(self):
        test_artists = ["Vorbis Artist 1", "Vorbis Artist 2"]
        test_metadata = {UnifiedMetadataKey.ARTISTS: test_artists}
        with temp_file_with_metadata({}, "flac") as test_file_path:
            update_metadata(test_file_path, test_metadata, metadata_format=MetadataFormat.VORBIS)
            metadata = get_unified_metadata(test_file_path)
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == test_artists

    def test_id3v1(self):
        test_artists = ["ID3v1 Artist"]
        test_metadata = {UnifiedMetadataKey.ARTISTS: test_artists}
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            update_metadata(test_file_path, test_metadata, metadata_format=MetadataFormat.ID3V1)
            metadata = get_unified_metadata(test_file_path)
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == test_artists

    def test_invalid_type_raises(self):
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file_path, {UnifiedMetadataKey.ARTISTS: "Single Artist"})
