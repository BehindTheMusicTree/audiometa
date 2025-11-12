"""End-to-end tests for rating normalization workflows.

These tests verify that the system correctly handles different rating scales and normalization values across different
audio formats.
"""

import pytest

from audiometa import delete_all_metadata, get_unified_metadata, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.e2e
class TestRatingWorkflows:
    def test_metadata_with_different_rating_normalizations(self):
        # Use external script to set initial metadata
        initial_metadata = {"title": "Initial Rating Test", "artist": "Initial Artist"}
        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # Test with 0-100 rating scale
            test_metadata_100 = {UnifiedMetadataKey.TITLE: "Rating Test 100", UnifiedMetadataKey.RATING: 60}
            update_metadata(
                test_file, test_metadata_100, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2
            )

            metadata_100 = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert metadata_100.get(UnifiedMetadataKey.TITLE) == "Rating Test 100"
            assert metadata_100.get(UnifiedMetadataKey.RATING) == 60

            # Test with 0-255 rating scale
            test_metadata_255 = {
                UnifiedMetadataKey.TITLE: "Rating Test 255",
                UnifiedMetadataKey.RATING: 153,  # 60% of 255
            }
            update_metadata(
                test_file, test_metadata_255, normalized_rating_max_value=255, metadata_format=MetadataFormat.ID3V2
            )

            metadata_255 = get_unified_metadata(test_file, normalized_rating_max_value=255)
            assert metadata_255.get(UnifiedMetadataKey.TITLE) == "Rating Test 255"
            assert metadata_255.get(UnifiedMetadataKey.RATING) == 153

    def test_rating_deletion_workflow(self):
        # E2E test for deleting ratings with different normalizations
        initial_metadata = {"title": "Rating Deletion Test", "artist": "Rating Deletion Artist"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Add rating with 100 scale
            rating_metadata_100 = {UnifiedMetadataKey.RATING: 80}
            update_metadata(
                test_file,
                rating_metadata_100,
                normalized_rating_max_value=100,
                metadata_format=MetadataFormat.ID3V2,
            )

            # 2. Verify rating was added
            metadata_with_rating = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert metadata_with_rating.get(UnifiedMetadataKey.RATING) == 80

            # 3. Delete rating by setting to None
            rating_deletion = {UnifiedMetadataKey.RATING: None}
            update_metadata(
                test_file, rating_deletion, normalized_rating_max_value=100, metadata_format=MetadataFormat.ID3V2
            )

            # 4. Verify rating was deleted
            metadata_after_deletion = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert metadata_after_deletion.get(UnifiedMetadataKey.RATING) is None

            # 5. Add rating with 255 scale
            rating_metadata_255 = {UnifiedMetadataKey.RATING: 204}  # 80% of 255
            update_metadata(
                test_file,
                rating_metadata_255,
                normalized_rating_max_value=255,
                metadata_format=MetadataFormat.ID3V2,
            )

            # 6. Verify rating was added with 255 scale
            metadata_with_rating_255 = get_unified_metadata(test_file, normalized_rating_max_value=255)
            assert metadata_with_rating_255.get(UnifiedMetadataKey.RATING) == 204

            # 7. Delete rating with 255 scale
            update_metadata(
                test_file, rating_deletion, normalized_rating_max_value=255, metadata_format=MetadataFormat.ID3V2
            )

            # 8. Verify rating was deleted
            final_metadata = get_unified_metadata(test_file, normalized_rating_max_value=255)
            assert final_metadata.get(UnifiedMetadataKey.RATING) is None

    def test_complete_rating_cleanup_workflow(self):
        # E2E test for complete cleanup including ratings
        initial_metadata = {"title": "Complete Rating Cleanup", "artist": "Complete Rating Artist"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Add comprehensive metadata including rating
            comprehensive_metadata = {
                UnifiedMetadataKey.RATING: 90,
                UnifiedMetadataKey.BPM: 130,
                UnifiedMetadataKey.COMMENT: "Rating cleanup test",
            }
            update_metadata(test_file, comprehensive_metadata, normalized_rating_max_value=100)

            # 2. Verify all metadata exists
            full_metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert full_metadata.get(UnifiedMetadataKey.RATING) == 90
            assert full_metadata.get(UnifiedMetadataKey.BPM) == 130
            assert full_metadata.get(UnifiedMetadataKey.COMMENT) == "Rating cleanup test"

            # 3. Delete all metadata including rating
            delete_result = delete_all_metadata(test_file)
            assert delete_result is True

            # 4. Verify all metadata including rating was deleted
            cleaned_metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert cleaned_metadata.get(UnifiedMetadataKey.RATING) is None
            assert cleaned_metadata.get(UnifiedMetadataKey.BPM) is None
            assert (
                cleaned_metadata.get(UnifiedMetadataKey.COMMENT) is None
                or cleaned_metadata.get(UnifiedMetadataKey.COMMENT) != "Rating cleanup test"
            )
