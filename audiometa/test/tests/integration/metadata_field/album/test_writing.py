import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestAlbumWriting:
    def test_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_album = "Test Album ID3v2"
            test_metadata = {UnifiedMetadataKey.ALBUM: test_album}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ALBUM) == test_album

    def test_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            test_album = "Test Album RIFF"
            test_metadata = {UnifiedMetadataKey.ALBUM: test_album}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.RIFF)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ALBUM) == test_album

    def test_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            test_album = "Test Album Vorbis"
            test_metadata = {UnifiedMetadataKey.ALBUM: test_album}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.VORBIS)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ALBUM) == test_album

    def test_id3v1(self):
        with temp_file_with_metadata({}, "id3v1") as test_file:
            test_album = "Test Album ID3v1"
            test_metadata = {UnifiedMetadataKey.ALBUM: test_album}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V1)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ALBUM) == test_album

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with temp_file_with_metadata({}, "mp3") as test_file:
            # pass an int where a string is expected
            bad_metadata = {UnifiedMetadataKey.ALBUM: 123}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file, bad_metadata)
