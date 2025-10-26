import pytest



from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata



from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat


@pytest.mark.integration
class TestRatingDeleting:
    def test_delete_rating_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 50}, metadata_format=MetadataFormat.ID3V2, normalized_rating_max_value=100)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) == 50
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) is None

    def test_delete_rating_id3v1(self):
        with TempFileWithMetadata({}, "id3v1") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError):
                update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 50}, metadata_format=MetadataFormat.ID3V1, normalized_rating_max_value=100)
            

    def test_delete_rating_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 50}, metadata_format=MetadataFormat.RIFF, normalized_rating_max_value=100)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) == 50
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) is None

    def test_delete_rating_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 50}, metadata_format=MetadataFormat.VORBIS, normalized_rating_max_value=100)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) == 50
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) is None

    def test_delete_rating_preserves_other_fields(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {
                UnifiedMetadataKey.RATING: 75,
                UnifiedMetadataKey.TITLE: "Test Title",
                UnifiedMetadataKey.ARTISTS: ["Test Artist"]
            }, normalized_rating_max_value=100)
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: None})
        
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) is None
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_rating_already_none(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: None})
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) is None

    def test_delete_rating_zero(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
        
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: 0}, normalized_rating_max_value=100)
            update_metadata(test_file.path, {UnifiedMetadataKey.RATING: None})
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) is None
