import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestDiscNumberDeleting:
    def test_delete_disc_number_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.DISC_NUMBER: 1, UnifiedMetadataKey.DISC_TOTAL: 2},
                metadata_format=MetadataFormat.ID3V2,
            )
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) == 1
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL) == 2

            update_metadata(test_file, {UnifiedMetadataKey.DISC_NUMBER: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL) is None

    def test_delete_disc_total_only_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.DISC_NUMBER: 1, UnifiedMetadataKey.DISC_TOTAL: 2},
                metadata_format=MetadataFormat.ID3V2,
            )
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) == 1
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL) == 2

            update_metadata(test_file, {UnifiedMetadataKey.DISC_TOTAL: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) == 1
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL) is None

    def test_delete_disc_number_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.DISC_NUMBER: 1, UnifiedMetadataKey.DISC_TOTAL: 2},
                metadata_format=MetadataFormat.VORBIS,
            )
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) == 1
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL) == 2

            update_metadata(test_file, {UnifiedMetadataKey.DISC_NUMBER: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL) is None

    def test_delete_disc_total_only_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.DISC_NUMBER: 1, UnifiedMetadataKey.DISC_TOTAL: 2},
                metadata_format=MetadataFormat.VORBIS,
            )
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) == 1
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL) == 2

            update_metadata(test_file, {UnifiedMetadataKey.DISC_TOTAL: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) == 1
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL) is None

    def test_delete_disc_number_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file,
                {
                    UnifiedMetadataKey.DISC_NUMBER: 1,
                    UnifiedMetadataKey.DISC_TOTAL: 2,
                    UnifiedMetadataKey.TITLE: "Test Title",
                    UnifiedMetadataKey.ARTISTS: ["Test Artist"],
                },
            )

            update_metadata(test_file, {UnifiedMetadataKey.DISC_NUMBER: None})

            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_disc_number_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.DISC_NUMBER: None})
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL) is None

    def test_delete_disc_number_zero(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.DISC_NUMBER: 0}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) == 0
            update_metadata(test_file, {UnifiedMetadataKey.DISC_NUMBER: None})
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER) is None
