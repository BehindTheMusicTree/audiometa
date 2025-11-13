import pytest

from audiometa import update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestFieldNotSupportedDeleting:
    def test_delete_field_not_supported_id3v2(self):
        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.ARCHIVAL_LOCATION metadata not supported by ID3v2 format",
            ),
        ):
            update_metadata(
                test_file, {UnifiedMetadataKey.ARCHIVAL_LOCATION: None}, metadata_format=MetadataFormat.ID3V2
            )

    def test_delete_field_not_supported_id3v1(self):
        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.ARCHIVAL_LOCATION metadata not supported by ID3v1 format",
            ),
        ):
            update_metadata(
                test_file, {UnifiedMetadataKey.ARCHIVAL_LOCATION: None}, metadata_format=MetadataFormat.ID3V1
            )

    def test_delete_field_not_supported_riff(self):
        with (
            temp_file_with_metadata({}, "wav") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.PUBLISHER metadata not supported by RIFF format",
            ),
        ):
            update_metadata(test_file, {UnifiedMetadataKey.PUBLISHER: None}, metadata_format=MetadataFormat.RIFF)

    def test_delete_field_not_supported_vorbis(self):
        with (
            temp_file_with_metadata({}, "flac") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.ARCHIVAL_LOCATION metadata not supported by Vorbis format",
            ),
        ):
            update_metadata(
                test_file, {UnifiedMetadataKey.ARCHIVAL_LOCATION: None}, metadata_format=MetadataFormat.VORBIS
            )
