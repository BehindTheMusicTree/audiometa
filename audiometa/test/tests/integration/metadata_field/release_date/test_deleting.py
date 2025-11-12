import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestReleaseDateDeleting:
    def test_delete_release_date_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file, {UnifiedMetadataKey.RELEASE_DATE: "2023-01-01"}, metadata_format=MetadataFormat.ID3V2
            )
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) == "2023-01-01"

            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) is None

    def test_delete_release_date_id3v1(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: "2023"}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) == "2023"

            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) is None

    def test_delete_release_date_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            update_metadata(
                test_file, {UnifiedMetadataKey.RELEASE_DATE: "2023-01-01"}, metadata_format=MetadataFormat.RIFF
            )
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) == "2023-01-01"

            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) is None

    def test_delete_release_date_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            update_metadata(
                test_file, {UnifiedMetadataKey.RELEASE_DATE: "2023-01-01"}, metadata_format=MetadataFormat.VORBIS
            )
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) == "2023-01-01"

            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) is None

    def test_delete_release_date_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file,
                {
                    UnifiedMetadataKey.RELEASE_DATE: "2023-01-01",
                    UnifiedMetadataKey.TITLE: "Test Title",
                    UnifiedMetadataKey.ARTISTS: ["Test Artist"],
                },
            )

            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: None})

            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_release_date_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: None})
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) is None

    def test_delete_release_date_empty_string(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: ""}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE) is None
