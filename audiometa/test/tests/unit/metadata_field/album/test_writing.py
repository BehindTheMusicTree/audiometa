
import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestAlbumWriting:
    def test_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            test_album = "Test Album ID3v2"
            test_metadata = {UnifiedMetadataKey.ALBUM: test_album}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            metadata = get_unified_metadata(test_file.path)
            assert metadata.get(UnifiedMetadataKey.ALBUM) == test_album

    def test_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            test_album = "Test Album RIFF"
            test_metadata = {UnifiedMetadataKey.ALBUM: test_album}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.RIFF)
            metadata = get_unified_metadata(test_file.path)
            assert metadata.get(UnifiedMetadataKey.ALBUM) == test_album

    def test_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            test_album = "Test Album Vorbis"
            test_metadata = {UnifiedMetadataKey.ALBUM: test_album}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.VORBIS)
            metadata = get_unified_metadata(test_file.path)
            assert metadata.get(UnifiedMetadataKey.ALBUM) == test_album

    def test_id3v1(self):
        with TempFileWithMetadata({}, "id3v1") as test_file:
            test_album = "Test Album ID3v1"
            test_metadata = {UnifiedMetadataKey.ALBUM: test_album}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V1)
            metadata = get_unified_metadata(test_file.path)
            assert metadata.get(UnifiedMetadataKey.ALBUM) == test_album

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with TempFileWithMetadata({}, "mp3") as test_file:
            # pass an int where a string is expected
            bad_metadata = {UnifiedMetadataKey.ALBUM: 123}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file.path, bad_metadata)
