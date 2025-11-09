import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.integration
class TestCommentDeleting:
    def test_delete_comment_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            ID3v2MetadataSetter.set_metadata(test_file_path, {"comment": "Test comment"})
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) == "Test comment"

            update_metadata(test_file_path, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) is None

    def test_delete_comment_id3v1(self):
        with temp_file_with_metadata({}, "id3v1") as test_file_path:
            ID3v1MetadataSetter.set_comment(test_file_path, "Test comment")
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) == "Test comment"

            update_metadata(test_file_path, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) is None

    def test_delete_comment_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file_path:
            RIFFMetadataSetter.set_comment(test_file_path, "Test comment")
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) == "Test comment"

            update_metadata(test_file_path, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) is None

    def test_delete_comment_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file_path:
            VorbisMetadataSetter.set_comment(test_file_path, "Test comment")
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) == "Test comment"

            update_metadata(test_file_path, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) is None

    def test_delete_comment_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            ID3v2MetadataSetter.set_metadata(test_file_path, {"comment": "Test comment"})
            ID3v2MetadataSetter.set_title(test_file_path, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file_path, "Test Artist")

            update_metadata(test_file_path, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V2)
            update_metadata(test_file_path, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V2)

            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) is None
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_comment_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            update_metadata(test_file_path, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) is None

    def test_delete_comment_empty_string(self):
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            ID3v2MetadataSetter.set_metadata(test_file_path, {"comment": ""})
            update_metadata(test_file_path, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COMMENT) is None
