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
class TestTitleDeleting:
    def test_delete_title_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_title(test_file, "Test Title")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.TITLE: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) is None

    def test_delete_title_id3v1(self):
        with temp_file_with_metadata({}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_title(test_file, "Test Title")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.TITLE: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) is None

    def test_delete_title_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_title(test_file, "Test Title")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.TITLE: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) is None

    def test_delete_title_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.add_title(test_file, "Test Title")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.TITLE: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) is None

    def test_delete_title_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_title(test_file, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file, "Test Artist")
            ID3v2MetadataSetter.set_album(test_file, "Test Album")

            # Delete only title using library API
            update_metadata(test_file, {UnifiedMetadataKey.TITLE: None}, metadata_format=MetadataFormat.ID3V2)

            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ALBUM) == "Test Album"

    def test_delete_title_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Try to delete title that doesn't exist
            update_metadata(test_file, {UnifiedMetadataKey.TITLE: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) is None

    def test_delete_title_empty_string(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.TITLE: ""}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) is None
