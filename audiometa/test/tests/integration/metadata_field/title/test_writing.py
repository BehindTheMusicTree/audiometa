"""Tests for writing title metadata using external scripts.

This refactored version uses external scripts instead of the app's update functions to prevent circular dependencies in
tests.
"""

import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestTitleWriting:
    def test_id3v2(self):
        test_title = "Test Title ID3v2"
        test_metadata = {"title": test_title}

        # Use external script to set metadata instead of app's update function
        with temp_file_with_metadata(test_metadata, "mp3") as test_file:
            # Now test that our reading logic works correctly
            title = get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE)
            assert title == test_title

    def test_riff(self):
        test_title = "Test Title RIFF"
        test_metadata = {"title": test_title}

        # Use external script to set metadata instead of app's update function
        with temp_file_with_metadata(test_metadata, "wav") as test_file:
            # Now test that our reading logic works correctly
            title = get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE)
            assert title == test_title

    def test_vorbis(self):
        test_title = "Test Title Vorbis"
        test_metadata = {"title": test_title}

        # Use external script to set metadata instead of app's update function
        with temp_file_with_metadata(test_metadata, "flac") as test_file:
            # Now test that our reading logic works correctly
            title = get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE)
            assert title == test_title

    def test_id3v1(self):
        from audiometa import update_metadata
        from audiometa.utils.metadata_format import MetadataFormat

        with temp_file_with_metadata({}, "mp3") as test_file:
            test_title = "Test Title ID3v1"
            test_metadata = {UnifiedMetadataKey.TITLE: test_title}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V1)
            title = get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE)
            assert title == test_title

    def test_invalid_type_raises(self):
        from audiometa import update_metadata
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with temp_file_with_metadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.TITLE: 123}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file, bad_metadata)
