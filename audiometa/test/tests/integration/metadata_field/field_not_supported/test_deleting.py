import pytest

from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata

from audiometa import update_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.exceptions import MetadataFieldNotSupportedByLib


@pytest.mark.integration
class TestFieldNotSupportedDeleting:
    def test_delete_field_not_supported_all_formats(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                update_metadata(test_file.path, {"FIELD_NOT_SUPPORTED": None})

    def test_delete_field_not_supported_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                update_metadata(test_file.path, {"FIELD_NOT_SUPPORTED": None}, metadata_format=MetadataFormat.ID3V2)

    def test_delete_field_not_supported_id3v1(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                update_metadata(test_file.path, {"FIELD_NOT_SUPPORTED": None}, metadata_format=MetadataFormat.ID3V1)

    def test_delete_field_not_supported_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
        
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                update_metadata(test_file.path, {"FIELD_NOT_SUPPORTED": None}, metadata_format=MetadataFormat.RIFF)

    def test_delete_field_not_supported_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
        
            with pytest.raises(MetadataFieldNotSupportedByLib, match="FIELD_NOT_SUPPORTED metadata not supported by the library."):
                update_metadata(test_file.path, {"FIELD_NOT_SUPPORTED": None}, metadata_format=MetadataFormat.VORBIS)