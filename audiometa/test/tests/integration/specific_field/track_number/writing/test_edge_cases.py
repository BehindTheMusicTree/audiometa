import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestTrackNumberWritingEdgeCases:
    def test_write_track_number_with_slash_format_id3v1(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            track_number_input = "5/12"
            test_metadata = {UnifiedMetadataKey.TRACK_NUMBER: track_number_input}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            track_number = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == '5'
            
    def test_write_track_number_with_slash_format_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            track_number_input = "5/12"
            test_metadata = {UnifiedMetadataKey.TRACK_NUMBER: track_number_input}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            track_number = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == '5/12'

    def test_write_track_number_simple_format_id3v1(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            track_number_input = "1"
            test_metadata = {UnifiedMetadataKey.TRACK_NUMBER: track_number_input}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            track_number = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == '1'
            
    def test_write_track_number_simple_format_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            track_number_input = "1"
            test_metadata = {UnifiedMetadataKey.TRACK_NUMBER: track_number_input}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            track_number = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == '1'
            
        
