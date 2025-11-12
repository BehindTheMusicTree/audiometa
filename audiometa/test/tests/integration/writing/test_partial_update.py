"""Tests for general metadata writing functionality using external scripts.

This refactored version uses external scripts to set up test data instead of the app's update functions, preventing
circular dependencies.
"""

import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestMetadataWriting:
    # Note: delete_all_metadata tests have been moved to test_delete_all_metadata.py

    def test_write_metadata_partial_update(self):
        # Use external script to set initial metadata
        initial_metadata = {"title": "Original Title", "artist": "Original Artist", "album": "Original Album"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # Get original metadata
            original_metadata = get_unified_metadata(test_file)
            original_album = original_metadata.get(UnifiedMetadataKey.ALBUM)

            # Update only title using app's function (this is what we're testing)
            test_metadata = {UnifiedMetadataKey.TITLE: "Partial Update Title"}

            update_metadata(test_file, test_metadata)
            updated_metadata = get_unified_metadata(test_file)

            # Title should be updated
            assert updated_metadata.get(UnifiedMetadataKey.TITLE) == "Partial Update Title"
            # Other fields should remain unchanged
            assert updated_metadata.get(UnifiedMetadataKey.ALBUM) == original_album
