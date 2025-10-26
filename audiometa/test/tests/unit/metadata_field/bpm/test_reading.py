

import pytest

from audiometa import get_unified_metadata_field
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestBpmReading:
    def test_id3v1(self):
        with TempFileWithMetadata({"title": "Test Song"}, "id3v1") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError):
                get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.ID3V1)

    def test_id3v2(self):
        with TempFileWithMetadata({"title": "Test Song", "bpm": 999}, "id3v2.4") as test_file:
            bpm = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.ID3V2)
            assert bpm == 999

    def test_vorbis(self):
        with TempFileWithMetadata({"title": "Test Song", "bpm": 999}, "flac") as test_file:
            bpm = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.VORBIS)
            assert bpm == 999

    def test_riff(self):
        with TempFileWithMetadata({"title": "Test Song", "bpm": 999}, "wav") as test_file:
            bpm = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.RIFF)
            assert bpm == 999
