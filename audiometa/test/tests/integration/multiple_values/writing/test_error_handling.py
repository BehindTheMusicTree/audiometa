from pathlib import Path

import pytest

from audiometa import update_metadata, get_unified_metadata_field
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.exceptions import InvalidMetadataFieldTypeError


@pytest.mark.integration
class TestMultipleValuesErrorHandling:
    def test_write_invalid_data_types_in_list(self, temp_audio_file: Path):
        # Test with invalid data types in multiple value lists
        metadata = {
            UnifiedMetadataKey.ARTISTS: [1, 2, 3]  # Numbers instead of strings
        }
        with pytest.raises(InvalidMetadataFieldTypeError):
            update_metadata(temp_audio_file, metadata)

    def test_write_mixed_data_types_in_list(self, temp_audio_file: Path):
        # Test with mixed data types in multiple value lists
        metadata = {
            UnifiedMetadataKey.ARTISTS: ["Artist One", 123, None, "Artist Two"]
        }
        with pytest.raises(InvalidMetadataFieldTypeError):
            update_metadata(temp_audio_file, metadata)
            
    def test_write_list_with_none_values_are_filtered(self, temp_audio_file: Path):
        # Test that None values in lists are automatically filtered out
        # If all values are None, the field should be removed entirely
        metadata = {
            UnifiedMetadataKey.ARTISTS: [None, None]
        }
        update_metadata(temp_audio_file, metadata)
        # Field should be removed (None) since all values were filtered out
        artists = get_unified_metadata_field(temp_audio_file, UnifiedMetadataKey.ARTISTS)
        assert artists is None
    
    def test_write_list_with_mixed_none_and_valid_values(self, temp_audio_file: Path):
        # Test that None values are filtered but valid values remain
        metadata = {
            UnifiedMetadataKey.ARTISTS: ["Artist One", None, "Artist Two", None, "Artist Three"]
        }
        update_metadata(temp_audio_file, metadata)
        # None values should be filtered out, only valid artists remain
        artists = get_unified_metadata_field(temp_audio_file, UnifiedMetadataKey.ARTISTS)
        assert artists == ["Artist One", "Artist Two", "Artist Three"]