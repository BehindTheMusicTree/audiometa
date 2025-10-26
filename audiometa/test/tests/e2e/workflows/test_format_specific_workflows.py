"""
End-to-end tests for format-specific metadata workflows.

These tests verify that the system works correctly with different audio formats
(MP3, FLAC, WAV) and their specific capabilities and limitations.
"""
import pytest

from audiometa import (
    get_unified_metadata,
    update_metadata,
    delete_all_metadata,
    get_bitrate,
    get_duration_in_sec
)
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.e2e
class TestFormatSpecificWorkflows:

    def test_complete_metadata_workflow_mp3(self):
        # Use external script to set initial metadata
        initial_metadata = {
            "title": "Initial MP3 Title",
            "artist": "Initial MP3 Artist",
            "album": "Initial MP3 Album"
        }
        with TempFileWithMetadata(initial_metadata, "mp3") as test_file:
            # 1. Read initial metadata
            initial_metadata_result = get_unified_metadata(test_file)
            assert isinstance(initial_metadata_result, dict)
            
            # 2. Update metadata using app's function (this is what we're testing)
            test_metadata = {
                UnifiedMetadataKey.TITLE: "Integration Test Title",
                UnifiedMetadataKey.ARTISTS: ["Integration Test Artist"],
                UnifiedMetadataKey.ALBUM: "Integration Test Album",
                UnifiedMetadataKey.RATING: 90,
                UnifiedMetadataKey.BPM: 130
            }
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100)
            
            # 3. Verify metadata was updated
            updated_metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert updated_metadata.get(UnifiedMetadataKey.TITLE) == "Integration Test Title"
            assert updated_metadata.get(UnifiedMetadataKey.ARTISTS) == ["Integration Test Artist"]
            assert updated_metadata.get(UnifiedMetadataKey.ALBUM) == "Integration Test Album"
            assert updated_metadata.get(UnifiedMetadataKey.RATING) == 90
            assert updated_metadata.get(UnifiedMetadataKey.BPM) == 130
            
            # 4. Test technical information
            bitrate = get_bitrate(test_file)
            duration = get_duration_in_sec(test_file)
            assert isinstance(bitrate, int)
            assert isinstance(duration, float)
            assert bitrate > 0
            assert duration > 0
            
            # 5. Delete metadata
            delete_result = delete_all_metadata(test_file)
            assert delete_result is True
            
            # 6. Verify metadata was deleted
            deleted_metadata = get_unified_metadata(test_file)
            # After deletion, metadata should be empty or minimal
            assert UnifiedMetadataKey.TITLE not in deleted_metadata or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "Integration Test Title"

    def test_complete_metadata_workflow_flac(self):
        # Use external script to set initial metadata
        initial_metadata = {
            "title": "Initial FLAC Title",
            "artist": "Initial FLAC Artist",
            "album": "Initial FLAC Album"
        }
        with TempFileWithMetadata(initial_metadata, "flac") as test_file:
            # 1. Read initial metadata
            initial_metadata_result = get_unified_metadata(test_file)
            assert isinstance(initial_metadata_result, dict)
            
            # 2. Update metadata using app's function (this is what we're testing)
            test_metadata = {
                UnifiedMetadataKey.TITLE: "FLAC Integration Test Title",
                UnifiedMetadataKey.ARTISTS: ["FLAC Integration Test Artist"],
                UnifiedMetadataKey.ALBUM: "FLAC Integration Test Album",
                UnifiedMetadataKey.RATING: 80,
                UnifiedMetadataKey.BPM: 140
            }
            update_metadata(test_file.path, test_metadata, normalized_rating_max_value=100)
            
            # 3. Verify metadata was updated
            updated_metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert updated_metadata.get(UnifiedMetadataKey.TITLE) == "FLAC Integration Test Title"
            assert updated_metadata.get(UnifiedMetadataKey.ARTISTS) == ["FLAC Integration Test Artist"]
            assert updated_metadata.get(UnifiedMetadataKey.ALBUM) == "FLAC Integration Test Album"
            assert updated_metadata.get(UnifiedMetadataKey.RATING) == 80
            assert updated_metadata.get(UnifiedMetadataKey.BPM) == 140
            
            # 4. Test technical information
            bitrate = get_bitrate(test_file)
            duration = get_duration_in_sec(test_file)
            assert isinstance(bitrate, int)
            assert isinstance(duration, float)
            assert bitrate > 0
            assert duration > 0

    def test_complete_metadata_workflow_wav(self):
        # Use external script to set initial metadata
        initial_metadata = {
            "title": "Initial WAV Title",
            "artist": "Initial WAV Artist",
            "album": "Initial WAV Album"
        }
        with TempFileWithMetadata(initial_metadata, "wav") as test_file:
            # 1. Read initial metadata
            initial_metadata_result = get_unified_metadata(test_file)
            assert isinstance(initial_metadata_result, dict)
            
            # 2. Update metadata using app's function (this is what we're testing)
            # WAV doesn't support rating or BPM
            test_metadata = {
                UnifiedMetadataKey.TITLE: "WAV Integration Test Title",
                UnifiedMetadataKey.ARTISTS: ["WAV Integration Test Artist"],
                UnifiedMetadataKey.ALBUM: "WAV Integration Test Album"
            }
            update_metadata(test_file.path, test_metadata)
            
            # 3. Verify metadata was updated
            updated_metadata = get_unified_metadata(test_file)
            assert updated_metadata.get(UnifiedMetadataKey.TITLE) == "WAV Integration Test Title"
            assert updated_metadata.get(UnifiedMetadataKey.ARTISTS) == ["WAV Integration Test Artist"]
            assert updated_metadata.get(UnifiedMetadataKey.ALBUM) == "WAV Integration Test Album"
            
            # 4. Test technical information
            bitrate = get_bitrate(test_file)
            duration = get_duration_in_sec(test_file)
            assert isinstance(bitrate, int)
            assert isinstance(duration, float)
            assert bitrate > 0
            assert duration > 0
