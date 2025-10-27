

import pytest

from audiometa import get_unified_metadata_field
from audiometa.exceptions import MetadataFieldNotSupportedByLib
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.utils.MetadataFormat import MetadataFormat


@pytest.mark.integration
class TestFieldNotSupportedReading:
    def test_field_not_supported_all_formats(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                get_unified_metadata_field(test_file.path, 'FIELD_NOT_SUPPORTED')

    def test_id3v1(self):
        with TempFileWithMetadata({"title": "Test Song"}, "id3v1") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                get_unified_metadata_field(test_file.path, 'FIELD_NOT_SUPPORTED', metadata_format=MetadataFormat.ID3V1)

    def test_id3v2(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                get_unified_metadata_field(test_file.path, 'FIELD_NOT_SUPPORTED', metadata_format=MetadataFormat.ID3V2)

    def test_vorbis(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                get_unified_metadata_field(test_file.path, 'FIELD_NOT_SUPPORTED', metadata_format=MetadataFormat.VORBIS)

    def test_riff(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                get_unified_metadata_field(test_file.path, 'FIELD_NOT_SUPPORTED', metadata_format=MetadataFormat.RIFF)
