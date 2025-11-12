import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestPublisherWriting:
    def test_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_publisher = "Test Publisher ID3v2"
            test_metadata = {UnifiedMetadataKey.PUBLISHER: test_publisher}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2)
            publisher = get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER)
            assert publisher == test_publisher

    def test_riff(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError

        with temp_file_with_metadata({}, "wav") as test_file:
            test_publisher = "Test Publisher RIFF"
            test_metadata = {UnifiedMetadataKey.PUBLISHER: test_publisher}

            # RIFF format raises exception for unsupported metadata
            with pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.PUBLISHER metadata not supported by RIFF format",
            ):
                update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.RIFF)

    def test_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            test_publisher = "Test Publisher Vorbis"
            test_metadata = {UnifiedMetadataKey.PUBLISHER: test_publisher}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.VORBIS)
            publisher = get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER)
            assert publisher == test_publisher

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with temp_file_with_metadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.PUBLISHER: 123}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file, bad_metadata)
