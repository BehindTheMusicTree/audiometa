import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestCommentWriting:
    def test_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_comment = "Test Comment ID3v2"
            test_metadata = {UnifiedMetadataKey.COMMENT: test_comment}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2)
            comment = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT)
            assert comment == test_comment

    def test_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            test_comment = "Test Comment RIFF"
            test_metadata = {UnifiedMetadataKey.COMMENT: test_comment}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.RIFF)
            comment = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT)
            assert comment == test_comment

    def test_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            test_comment = "Test Comment Vorbis"
            test_metadata = {UnifiedMetadataKey.COMMENT: test_comment}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.VORBIS)
            comment = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT)
            assert comment == test_comment

    def test_id3v1(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_comment = "Test Comment ID3v1"
            test_metadata = {UnifiedMetadataKey.COMMENT: test_comment}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V1)
            comment = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT)
            assert comment == test_comment

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with temp_file_with_metadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.COMMENT: 12345}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file, bad_metadata)
