import pytest



from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata



from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat


@pytest.mark.integration
class TestReleaseDateDeleting:
    def test_delete_release_date_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: "2023-01-01"}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) == "2023-01-01"
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) is None

    def test_delete_release_date_id3v1(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: "2023"}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) == "2023"
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: None}, metadata_format=MetadataFormat.ID3V1)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) is None

    def test_delete_release_date_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: "2023-01-01"}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) == "2023-01-01"
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) is None

    def test_delete_release_date_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: "2023-01-01"}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) == "2023-01-01"
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) is None

    def test_delete_release_date_preserves_other_fields(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {
                UnifiedMetadataKey.RELEASE_DATE: "2023-01-01",
                UnifiedMetadataKey.TITLE: "Test Title",
                UnifiedMetadataKey.ARTISTS: ["Test Artist"]
            })
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: None})
        
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) is None
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_release_date_already_none(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: None})
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) is None

    def test_delete_release_date_empty_string(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: ""})
            update_metadata(test_file.path, {UnifiedMetadataKey.RELEASE_DATE: None})
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE) is None
