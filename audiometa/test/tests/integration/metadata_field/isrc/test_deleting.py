"""Tests for deleting ISRC metadata field."""

import pytest

from audiometa import delete_all_metadata, get_unified_metadata_field
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestISRCDeleting:
    def test_id3v2_isrc_deleted_with_all_metadata(self):
        """Test that ISRC is deleted when deleting all metadata from MP3."""
        with temp_file_with_metadata({"isrc": "USRC17607839"}, "mp3") as test_file:
            delete_all_metadata(test_file)
            isrc = get_unified_metadata_field(test_file, UnifiedMetadataKey.ISRC)
            assert isrc is None

    def test_vorbis_isrc_deleted_with_all_metadata(self):
        """Test that ISRC is deleted when deleting all metadata from FLAC."""
        with temp_file_with_metadata({"isrc": "GBUM71505078"}, "flac") as test_file:
            delete_all_metadata(test_file)
            isrc = get_unified_metadata_field(test_file, UnifiedMetadataKey.ISRC)
            assert isrc is None

    def test_riff_isrc_deleted_with_all_metadata(self):
        """Test that ISRC is deleted when deleting all metadata from WAV."""
        with temp_file_with_metadata({"isrc": "FRXM01500014"}, "wav") as test_file:
            delete_all_metadata(test_file)
            isrc = get_unified_metadata_field(test_file, UnifiedMetadataKey.ISRC)
            assert isrc is None
