import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.exceptions import InvalidMetadataFieldTypeError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestMultipleValuesErrorHandling:
    def test_write_invalid_data_types_in_list(self):
        # Test with invalid data types in multiple value lists
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            metadata = {UnifiedMetadataKey.ARTISTS: [1, 2, 3]}  # Numbers instead of strings
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(temp_audio_file_path, metadata)

    def test_write_mixed_data_types_in_list(self):
        # Test with mixed data types in multiple value lists
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            metadata = {UnifiedMetadataKey.ARTISTS: ["Artist One", 123, None, "Artist Two"]}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(temp_audio_file_path, metadata)

    def test_write_list_with_none_values_are_filtered(self):
        # Test that None values in lists are automatically filtered out
        # If all values are None, the field should be removed entirely
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            metadata = {UnifiedMetadataKey.ARTISTS: [None, None]}
            update_metadata(temp_audio_file_path, metadata)
            # Field should be removed (None) since all values were filtered out
            artists = get_unified_metadata_field(temp_audio_file_path, UnifiedMetadataKey.ARTISTS)
            assert artists is None

    def test_write_list_with_mixed_none_and_valid_values(self):
        # Test that None values are filtered but valid values remain
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            metadata = {UnifiedMetadataKey.ARTISTS: ["Artist One", None, "Artist Two", None, "Artist Three"]}
            update_metadata(temp_audio_file_path, metadata)
            # None values should be filtered out, only valid artists remain
            artists = get_unified_metadata_field(temp_audio_file_path, UnifiedMetadataKey.ARTISTS)
            assert artists == ["Artist One", "Artist Two", "Artist Three"]
