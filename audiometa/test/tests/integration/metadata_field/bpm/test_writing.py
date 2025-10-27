import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestBpmWriting:
    def test_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            test_bpm = 128
            test_metadata = {UnifiedMetadataKey.BPM: test_bpm}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            bpm = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM)
            assert bpm == test_bpm

    def test_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            test_bpm = 120
            test_metadata = {UnifiedMetadataKey.BPM: test_bpm}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.RIFF)
            
            raw_metadata = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM)
            assert raw_metadata == test_bpm

    def test_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            test_bpm = 140
            test_metadata = {UnifiedMetadataKey.BPM: test_bpm}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.VORBIS)
            bpm = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM)
            assert bpm == test_bpm

    def test_id3v1(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
        
        with TempFileWithMetadata({}, "mp3") as test_file:
            test_bpm = 128
            test_metadata = {UnifiedMetadataKey.BPM: test_bpm}
        
            # ID3v1 format raises exception for unsupported metadata when format is forced
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError, match="UnifiedMetadataKey.BPM metadata not supported by this format"):
                update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V1)

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with TempFileWithMetadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.BPM: "not-an-int"}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file.path, bad_metadata)
