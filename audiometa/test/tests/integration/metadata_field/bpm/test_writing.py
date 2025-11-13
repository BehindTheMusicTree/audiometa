import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestBpmWriting:
    def test_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_bpm = 128
            test_metadata = {UnifiedMetadataKey.BPM: test_bpm}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2)
            bpm = get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM)
            assert bpm == test_bpm

    def test_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            test_bpm = 120
            test_metadata = {UnifiedMetadataKey.BPM: test_bpm}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.RIFF)

            raw_metadata = get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM)
            assert raw_metadata == test_bpm

    def test_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            test_bpm = 140
            test_metadata = {UnifiedMetadataKey.BPM: test_bpm}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.VORBIS)
            bpm = get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM)
            assert bpm == test_bpm

    def test_id3v1(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError

        with temp_file_with_metadata({}, "mp3") as test_file:
            test_bpm = 128
            test_metadata = {UnifiedMetadataKey.BPM: test_bpm}

            # ID3v1 format raises exception for unsupported metadata when format is forced
            with pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.BPM metadata not supported by ID3v1 format",
            ):
                update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V1)

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with temp_file_with_metadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.BPM: "not-an-int"}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file, bad_metadata)
