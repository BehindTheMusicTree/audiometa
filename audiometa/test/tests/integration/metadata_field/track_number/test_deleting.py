import pytest



from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata



from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat


@pytest.mark.integration
class TestTrackNumberDeleting:
    def test_delete_track_number_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.TRACK_NUMBER: 5}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER) == 5
        
            update_metadata(test_file.path, {UnifiedMetadataKey.TRACK_NUMBER: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER) is None

    def test_delete_track_number_id3v1(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.TRACK_NUMBER: 3}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER) == 3
        
            update_metadata(test_file.path, {UnifiedMetadataKey.TRACK_NUMBER: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER) is None

    def test_delete_track_number_preserves_other_fields(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {
                UnifiedMetadataKey.TRACK_NUMBER: 7,
                UnifiedMetadataKey.TITLE: "Test Title",
                UnifiedMetadataKey.ARTISTS: ["Test Artist"]
            })
        
            update_metadata(test_file.path, {UnifiedMetadataKey.TRACK_NUMBER: None})
        
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER) is None
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_track_number_already_none(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.TRACK_NUMBER: None})
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER) is None

    def test_delete_track_number_zero(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.TRACK_NUMBER: 0})
            update_metadata(test_file.path, {UnifiedMetadataKey.TRACK_NUMBER: None})
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER) is None
