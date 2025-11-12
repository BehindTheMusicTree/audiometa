import pytest

from audiometa import update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByLibError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat


@pytest.mark.integration
class TestFieldNotSupportedWriting:
    def test_id3v1(self):
        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByLibError, match="FIELD_NOT_SUPPORTED metadata not supported by the library."
            ),
        ):
            update_metadata(
                test_file,
                {"FIELD_NOT_SUPPORTED": "Test Field Not Supported"},
                metadata_format=MetadataFormat.ID3V1,
            )

    def test_id3v2(self):
        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByLibError, match="FIELD_NOT_SUPPORTED metadata not supported by the library."
            ),
        ):
            update_metadata(
                test_file,
                {"FIELD_NOT_SUPPORTED": "Test Field Not Supported"},
                metadata_format=MetadataFormat.ID3V2,
            )

    def test_riff(self):
        with (
            temp_file_with_metadata({}, "wav") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByLibError, match="FIELD_NOT_SUPPORTED metadata not supported by the library."
            ),
        ):
            update_metadata(
                test_file,
                {"FIELD_NOT_SUPPORTED": "Test Field Not Supported"},
                metadata_format=MetadataFormat.RIFF,
            )

    def test_vorbis(self):
        with (
            temp_file_with_metadata({}, "flac") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByLibError, match="FIELD_NOT_SUPPORTED metadata not supported by the library."
            ),
        ):
            update_metadata(
                test_file,
                {"FIELD_NOT_SUPPORTED": "Test Field Not Supported"},
                metadata_format=MetadataFormat.VORBIS,
            )
