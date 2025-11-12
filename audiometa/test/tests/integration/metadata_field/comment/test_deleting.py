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
class TestCommentDeleting:
    def test_delete_comment_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_metadata(test_file, {"comment": "Test comment"})
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) == "Test comment"

            update_metadata(test_file, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) is None

    def test_delete_comment_id3v1(self):
        with temp_file_with_metadata({}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_comment(test_file, "Test comment")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) == "Test comment"

            update_metadata(test_file, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) is None

    def test_delete_comment_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_comment(test_file, "Test comment")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) == "Test comment"

            update_metadata(test_file, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) is None

    def test_delete_comment_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_comment(test_file, "Test comment")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) == "Test comment"

            update_metadata(test_file, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) is None

    def test_delete_comment_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_metadata(test_file, {"comment": "Test comment"})
            ID3v2MetadataSetter.set_title(test_file, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file, "Test Artist")

            update_metadata(test_file, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V2)
            update_metadata(test_file, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V2)

            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_comment_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) is None

    def test_delete_comment_empty_string(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.COMMENT: ""}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT) is None
