import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestCommentWriting:
    def test_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            test_comment = "Test Comment ID3v2"
            test_metadata = {UnifiedMetadataKey.COMMENT: test_comment}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            comment = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COMMENT)
            assert comment == test_comment

    def test_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            test_comment = "Test Comment RIFF"
            test_metadata = {UnifiedMetadataKey.COMMENT: test_comment}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.RIFF)
            comment = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COMMENT)
            assert comment == test_comment

    def test_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            test_comment = "Test Comment Vorbis"
            test_metadata = {UnifiedMetadataKey.COMMENT: test_comment}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.VORBIS)
            comment = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COMMENT)
            assert comment == test_comment

    def test_id3v1(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            test_comment = "Test Comment ID3v1"
            test_metadata = {UnifiedMetadataKey.COMMENT: test_comment}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V1)
            comment = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COMMENT)
            assert comment == test_comment

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with TempFileWithMetadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.COMMENT: 12345}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file.path, bad_metadata)
