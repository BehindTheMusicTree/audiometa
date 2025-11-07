import pytest

from audiometa import (
    update_metadata,
    get_unified_metadata,
)
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataWritingStrategy import MetadataWritingStrategy
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.integration
class TestStrategySpecific:

    def test_fail_on_unsupported_field_preserve_strategy(self):
        initial_metadata = {
            "title": "Original WAV Title",
            "artist": "Original WAV Artist"
        }
        with temp_file_with_metadata(initial_metadata, "wav") as test_file_path:
            initial_read = get_unified_metadata(test_file_path)
            assert initial_read.get(UnifiedMetadataKey.TITLE) == "Original WAV Title"
            assert initial_read.get(UnifiedMetadataKey.ARTISTS) == ["Original WAV Artist"]
            
            test_metadata = {
                UnifiedMetadataKey.TITLE: "New WAV Title",  # Should NOT be written
                UnifiedMetadataKey.ARTISTS: ["New WAV Artist"],  # Should NOT be written
                UnifiedMetadataKey.REPLAYGAIN: "89 dB"  # Not supported by RIFF format
            }
            
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError) as exc_info:
                update_metadata(test_file_path, test_metadata, 
                                   metadata_strategy=MetadataWritingStrategy.PRESERVE,
                                   fail_on_unsupported_field=True)
            
            assert "Fields not supported by riff format" in str(exc_info.value)
            assert "REPLAYGAIN" in str(exc_info.value)
            
            final_read = get_unified_metadata(test_file_path)
            assert final_read.get(UnifiedMetadataKey.TITLE) == "Original WAV Title"  # Should be unchanged
            assert final_read.get(UnifiedMetadataKey.ARTISTS) == ["Original WAV Artist"]  # Should be unchanged
            assert final_read.get(UnifiedMetadataKey.REPLAYGAIN) is None  # Should not exist

    def test_fail_on_unsupported_field_cleanup_strategy(self):
        initial_metadata = {
            "title": "Original WAV Title",
            "artist": "Original WAV Artist"
        }
        with temp_file_with_metadata(initial_metadata, "wav") as test_file_path:
            initial_read = get_unified_metadata(test_file_path)
            assert initial_read.get(UnifiedMetadataKey.TITLE) == "Original WAV Title"
            assert initial_read.get(UnifiedMetadataKey.ARTISTS) == ["Original WAV Artist"]
            
            test_metadata = {
                UnifiedMetadataKey.TITLE: "New WAV Title",  # Should NOT be written
                UnifiedMetadataKey.ARTISTS: ["New WAV Artist"],  # Should NOT be written
                UnifiedMetadataKey.REPLAYGAIN: "89 dB"  # Not supported by RIFF format
            }
            
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError) as exc_info:
                update_metadata(test_file_path, test_metadata, 
                                   metadata_strategy=MetadataWritingStrategy.CLEANUP,
                                   fail_on_unsupported_field=True)
            
            assert "Fields not supported by riff format" in str(exc_info.value)
            assert "REPLAYGAIN" in str(exc_info.value)
            
            final_read = get_unified_metadata(test_file_path)
            assert final_read.get(UnifiedMetadataKey.TITLE) == "Original WAV Title"  # Should be unchanged
            assert final_read.get(UnifiedMetadataKey.ARTISTS) == ["Original WAV Artist"]  # Should be unchanged
            assert final_read.get(UnifiedMetadataKey.REPLAYGAIN) is None  # Should not exist

    def test_fail_on_unsupported_field_sync_strategy(self):
        initial_metadata = {
            "title": "Original WAV Title",
            "artist": "Original WAV Artist"
        }
        with temp_file_with_metadata(initial_metadata, "wav") as test_file_path:
            initial_read = get_unified_metadata(test_file_path)
            assert initial_read.get(UnifiedMetadataKey.TITLE) == "Original WAV Title"
            assert initial_read.get(UnifiedMetadataKey.ARTISTS) == ["Original WAV Artist"]
            
            test_metadata = {
                UnifiedMetadataKey.TITLE: "New WAV Title",  # Should be written to RIFF (supported)
                UnifiedMetadataKey.ARTISTS: ["New WAV Artist"],  # Should be written to RIFF (supported)
                UnifiedMetadataKey.REPLAYGAIN: "89 dB"  # Not supported by RIFF format - should cause failure
            }
            
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError) as exc_info:
                update_metadata(test_file_path, test_metadata, 
                                   metadata_strategy=MetadataWritingStrategy.SYNC,
                                   fail_on_unsupported_field=True)
            
            assert "Fields not supported by riff format" in str(exc_info.value)
            assert "REPLAYGAIN" in str(exc_info.value)
            
            # With fail_on_unsupported_field=True, the operation should be atomic
            # No writing should occur, so file should remain unchanged
            final_read = get_unified_metadata(test_file_path)
            assert final_read.get(UnifiedMetadataKey.TITLE) == "Original WAV Title"  # Should be unchanged
            assert final_read.get(UnifiedMetadataKey.ARTISTS) == ["Original WAV Artist"]  # Should be unchanged
            assert final_read.get(UnifiedMetadataKey.REPLAYGAIN) is None  # Should not exist

