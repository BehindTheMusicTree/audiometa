import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByLib
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestFieldNotSupportedWriting:
    def test_id3v1(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                update_metadata(test_file.path, {"FIELD_NOT_SUPPORTED": "Test Field Not Supported"}, metadata_format=MetadataFormat.ID3V1)
    
    def test_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                update_metadata(test_file.path, {"FIELD_NOT_SUPPORTED": "Test Field Not Supported"}, metadata_format=MetadataFormat.ID3V2)

    def test_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                update_metadata(test_file.path, {"FIELD_NOT_SUPPORTED": "Test Field Not Supported"}, metadata_format=MetadataFormat.RIFF)

    def test_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                update_metadata(test_file.path, {"FIELD_NOT_SUPPORTED": "Test Field Not Supported"}, metadata_format=MetadataFormat.VORBIS)
