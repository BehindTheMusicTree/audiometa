import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestPublisherDeleting:
    def test_delete_publisher_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file, {UnifiedMetadataKey.PUBLISHER: "Test Publisher"}, metadata_format=MetadataFormat.ID3V2
            )
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER) == "Test Publisher"

            update_metadata(test_file, {UnifiedMetadataKey.PUBLISHER: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER) is None

    def test_delete_publisher_id3v1(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError

        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.PUBLISHER metadata not supported by ID3v1 format",
            ),
        ):
            update_metadata(
                test_file,
                {UnifiedMetadataKey.PUBLISHER: "Test Publisher"},
                metadata_format=MetadataFormat.ID3V1,
            )

    def test_delete_publisher_riff(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError

        with (
            temp_file_with_metadata({}, "wav") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.PUBLISHER metadata not supported by RIFF format",
            ),
        ):
            update_metadata(
                test_file,
                {UnifiedMetadataKey.PUBLISHER: "Test Publisher"},
                metadata_format=MetadataFormat.RIFF,
            )

    def test_delete_publisher_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            update_metadata(
                test_file, {UnifiedMetadataKey.PUBLISHER: "Test Publisher"}, metadata_format=MetadataFormat.VORBIS
            )
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER) == "Test Publisher"

            update_metadata(test_file, {UnifiedMetadataKey.PUBLISHER: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER) is None

    def test_delete_publisher_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file,
                {
                    UnifiedMetadataKey.PUBLISHER: "Test Publisher",
                    UnifiedMetadataKey.TITLE: "Test Title",
                    UnifiedMetadataKey.ARTISTS: ["Test Artist"],
                },
            )

            update_metadata(test_file, {UnifiedMetadataKey.PUBLISHER: None})

            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_publisher_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.PUBLISHER: None})
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER) is None

    def test_delete_publisher_empty_string(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.PUBLISHER: ""}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER) is None
