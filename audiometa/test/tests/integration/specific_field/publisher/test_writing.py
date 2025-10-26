import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestPublisherWriting:
    def test_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            test_publisher = "Test Publisher ID3v2"
            test_metadata = {UnifiedMetadataKey.PUBLISHER: test_publisher}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            publisher = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.PUBLISHER)
            assert publisher == test_publisher

    def test_riff(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
        
        with TempFileWithMetadata({}, "wav") as test_file:
            test_publisher = "Test Publisher RIFF"
            test_metadata = {UnifiedMetadataKey.PUBLISHER: test_publisher}
        
            # RIFF format raises exception for unsupported metadata
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError, match="UnifiedMetadataKey.PUBLISHER metadata not supported by RIFF format"):
                update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.RIFF)

    def test_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            test_publisher = "Test Publisher Vorbis"
            test_metadata = {UnifiedMetadataKey.PUBLISHER: test_publisher}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.VORBIS)
            publisher = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.PUBLISHER)
            assert publisher == test_publisher

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with TempFileWithMetadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.PUBLISHER: 123}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file.path, bad_metadata)
