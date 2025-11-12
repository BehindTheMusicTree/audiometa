"""End-to-end tests for core metadata editing workflows.

These tests verify the basic functionality of the entire system for real users, including file I/O and complete metadata
editing workflows.
"""

from pathlib import Path

import pytest

from audiometa import (
    _AudioFile,
    delete_all_metadata,
    get_bitrate,
    get_duration_in_sec,
    get_unified_metadata,
    update_metadata,
)
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.e2e
class TestCoreWorkflows:
    def test_complete_metadata_editing_workflow(self):
        # This is an e2e test - it tests the entire user journey
        # 1. Load a file
        # 2. Read existing metadata
        # 3. Edit multiple fields
        # 4. Save changes
        # 5. Verify persistence

        # Use external script to set initial metadata
        initial_metadata = {"title": "Original Title", "artist": "Original Artist", "album": "Original Album"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # Edit metadata using app's function (this is what we're testing)
            test_metadata = {
                UnifiedMetadataKey.TITLE: "New Title",
                UnifiedMetadataKey.ARTISTS: ["New Artist"],
                UnifiedMetadataKey.ALBUM: "New Album",
                UnifiedMetadataKey.GENRES_NAMES: ["Rock"],
                UnifiedMetadataKey.COMMENT: "Test comment",
            }

            # Save changes
            update_metadata(test_file, test_metadata)

            # Verify persistence by reloading
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "New Title"
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["New Artist"]
            assert metadata.get(UnifiedMetadataKey.ALBUM) == "New Album"
            assert metadata.get(UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]
            assert metadata.get(UnifiedMetadataKey.COMMENT) == "Test comment"

    def test_batch_metadata_processing(self, sample_mp3_file, sample_flac_file, sample_wav_file):
        # E2E test for batch operations
        results = []

        sample_files = [(sample_mp3_file, "mp3"), (sample_flac_file, "flac"), (sample_wav_file, "wav")]

        for file_path, format_type in sample_files:
            try:
                # Set initial metadata using external script
                initial_metadata = {"title": "Batch Test Title", "artist": "Batch Test Artist"}
                with temp_file_with_metadata(initial_metadata, format_type) as test_file:
                    # Update metadata using functional API (this is what we're testing)
                    test_metadata = {
                        UnifiedMetadataKey.ALBUM: "Batch Album",
                        UnifiedMetadataKey.COMMENT: "Batch processing test",
                    }
                    update_metadata(test_file, test_metadata)
                    results.append(("success", file_path))
            except Exception as e:
                results.append(("error", file_path, str(e)))

        # Verify all files were processed
        assert len(results) == len(sample_files)
        success_count = sum(1 for result in results if result[0] == "success")
        assert success_count > 0

    def test_audio_file_context_manager(self, sample_mp3_file: Path):
        with _AudioFile(sample_mp3_file) as audio_file:
            # Test that we can read metadata within context using file path
            metadata = get_unified_metadata(audio_file.file_path)
            assert isinstance(metadata, dict)

            # Test that we can get technical info within context using file path
            bitrate = get_bitrate(audio_file.file_path)
            duration = get_duration_in_sec(audio_file.file_path)
            assert isinstance(bitrate, int)
            assert isinstance(duration, float)

    def test_cross_format_deletion_workflow(self, sample_mp3_file, sample_flac_file, sample_wav_file):
        # E2E test for deletion across multiple formats
        test_metadata = {
            UnifiedMetadataKey.TITLE: "Cross Format Deletion",
            UnifiedMetadataKey.ARTISTS: ["Cross Format Artist"],
            UnifiedMetadataKey.ALBUM: "Cross Format Album",
        }

        sample_files = [(sample_mp3_file, "mp3"), (sample_flac_file, "flac"), (sample_wav_file, "wav")]

        for _file_path, format_type in sample_files:
            # Set up metadata using external script
            initial_metadata = {"title": "Original Title", "artist": "Original Artist"}
            with temp_file_with_metadata(initial_metadata, format_type) as test_file:
                # Add metadata using app's function
                update_metadata(test_file, test_metadata)

                # Verify metadata was added
                added_metadata = get_unified_metadata(test_file)
                assert added_metadata.get(UnifiedMetadataKey.TITLE) == "Cross Format Deletion"

                # Delete all metadata
                delete_result = delete_all_metadata(test_file)
                assert delete_result is True

                # Verify metadata was deleted
                deleted_metadata = get_unified_metadata(test_file)
                assert (
                    deleted_metadata.get(UnifiedMetadataKey.TITLE) is None
                    or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "Cross Format Deletion"
                )

    def test_metadata_cleanup_workflow(self):
        # E2E test for complete metadata cleanup workflow
        initial_metadata = {
            "title": "Cleanup Test Title",
            "artist": "Cleanup Test Artist",
            "album": "Cleanup Test Album",
            "year": "2023",
            "genre": "Electronic",
        }

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Cleanup Test Title"

            # 2. Add more metadata
            additional_metadata = {
                UnifiedMetadataKey.RATING: 80,
                UnifiedMetadataKey.BPM: 128,
                UnifiedMetadataKey.COMMENT: "Cleanup test comment",
            }
            update_metadata(test_file, additional_metadata, normalized_rating_max_value=100)

            # 3. Verify all metadata exists
            full_metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert full_metadata.get(UnifiedMetadataKey.RATING) == 80
            assert full_metadata.get(UnifiedMetadataKey.BPM) == 128

            # 4. Complete cleanup - delete all metadata
            delete_result = delete_all_metadata(test_file)
            assert delete_result is True

            # 5. Verify complete cleanup
            cleaned_metadata = get_unified_metadata(test_file)
            assert (
                cleaned_metadata.get(UnifiedMetadataKey.TITLE) is None
                or cleaned_metadata.get(UnifiedMetadataKey.TITLE) != "Cleanup Test Title"
            )
            assert cleaned_metadata.get(UnifiedMetadataKey.RATING) is None
            assert cleaned_metadata.get(UnifiedMetadataKey.BPM) is None
