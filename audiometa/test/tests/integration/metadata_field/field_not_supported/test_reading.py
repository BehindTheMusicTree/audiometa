import pytest

from audiometa import get_unified_metadata_field
from audiometa.exceptions import MetadataFieldNotSupportedByLibError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat


@pytest.mark.integration
class TestFieldNotSupportedReading:
    def test_field_not_supported_all_formats(self):
        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByLibError, match="FIELD_NOT_SUPPORTED metadata not supported by the library."
            ),
        ):
            get_unified_metadata_field(test_file, "FIELD_NOT_SUPPORTED")

    def test_id3v1(self):
        with (
            temp_file_with_metadata({"title": "Test Song"}, "id3v1") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByLibError, match="FIELD_NOT_SUPPORTED metadata not supported by the library."
            ),
        ):
            get_unified_metadata_field(test_file, "FIELD_NOT_SUPPORTED", metadata_format=MetadataFormat.ID3V1)

    def test_id3v2(self):
        with (
            temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByLibError, match="FIELD_NOT_SUPPORTED metadata not supported by the library."
            ),
        ):
            get_unified_metadata_field(test_file, "FIELD_NOT_SUPPORTED", metadata_format=MetadataFormat.ID3V2)

    def test_vorbis(self):
        with (
            temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByLibError, match="FIELD_NOT_SUPPORTED metadata not supported by the library."
            ),
        ):
            get_unified_metadata_field(test_file, "FIELD_NOT_SUPPORTED", metadata_format=MetadataFormat.VORBIS)

    def test_riff(self):
        with (
            temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByLibError, match="FIELD_NOT_SUPPORTED metadata not supported by the library."
            ),
        ):
            get_unified_metadata_field(test_file, "FIELD_NOT_SUPPORTED", metadata_format=MetadataFormat.RIFF)
