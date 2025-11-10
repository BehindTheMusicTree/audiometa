import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.integration
class TestCopyrightDeleting:
    def test_delete_copyright_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            update_metadata(
                test_file_path, {UnifiedMetadataKey.COPYRIGHT: "Test Copyright"}, metadata_format=MetadataFormat.ID3V2
            )
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COPYRIGHT) == "Test Copyright"

            update_metadata(test_file_path, {UnifiedMetadataKey.COPYRIGHT: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COPYRIGHT) is None

    def test_delete_copyright_id3v1(self):
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            with pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.COPYRIGHT metadata not supported by this format",
            ):
                update_metadata(
                    test_file_path,
                    {UnifiedMetadataKey.COPYRIGHT: "Test Copyright"},
                    metadata_format=MetadataFormat.ID3V1,
                )

    def test_delete_copyright_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file_path:
            update_metadata(
                test_file_path, {UnifiedMetadataKey.COPYRIGHT: "Test Copyright"}, metadata_format=MetadataFormat.RIFF
            )
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COPYRIGHT) == "Test Copyright"

            update_metadata(test_file_path, {UnifiedMetadataKey.COPYRIGHT: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COPYRIGHT) is None

    def test_delete_copyright_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file_path:
            update_metadata(
                test_file_path, {UnifiedMetadataKey.COPYRIGHT: "Test Copyright"}, metadata_format=MetadataFormat.VORBIS
            )
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COPYRIGHT) == "Test Copyright"

            update_metadata(test_file_path, {UnifiedMetadataKey.COPYRIGHT: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COPYRIGHT) is None

    def test_delete_copyright_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            update_metadata(
                test_file_path,
                {
                    UnifiedMetadataKey.COPYRIGHT: "Test Copyright",
                    UnifiedMetadataKey.TITLE: "Test Title",
                    UnifiedMetadataKey.ARTISTS: ["Test Artist"],
                },
            )

            update_metadata(test_file_path, {UnifiedMetadataKey.COPYRIGHT: None})

            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COPYRIGHT) is None
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_copyright_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            update_metadata(test_file_path, {UnifiedMetadataKey.COPYRIGHT: None})
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COPYRIGHT) is None

    def test_delete_copyright_empty_string(self):
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            update_metadata(test_file_path, {UnifiedMetadataKey.COPYRIGHT: ""})
            update_metadata(test_file_path, {UnifiedMetadataKey.COPYRIGHT: None})
            assert get_unified_metadata_field(test_file_path, UnifiedMetadataKey.COPYRIGHT) is None
