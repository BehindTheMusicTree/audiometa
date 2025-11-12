import pytest

from audiometa import get_unified_metadata_field
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestBpmReading:
    def test_id3v1(self):
        with (
            temp_file_with_metadata({"title": "Test Song"}, "id3v1") as test_file,
            pytest.raises(MetadataFieldNotSupportedByMetadataFormatError),
        ):
            get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.ID3V1)

    def test_id3v2(self):
        with temp_file_with_metadata({"title": "Test Song", "bpm": 999}, "id3v2.4") as test_file:
            bpm = get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.ID3V2)
            assert bpm == 999

    def test_vorbis(self):
        with temp_file_with_metadata({"title": "Test Song", "bpm": 999}, "flac") as test_file:
            bpm = get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.VORBIS)
            assert bpm == 999

    def test_riff(self):
        with temp_file_with_metadata({"title": "Test Song", "bpm": 999}, "wav") as test_file:
            bpm = get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.RIFF)
            assert bpm == 999
