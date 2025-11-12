"""Tests for CLEANUP metadata writing strategy.

This module tests the CLEANUP strategy which writes to native format and removes all non-native metadata formats.
"""

import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.test.helpers.id3v1.id3v1_metadata_setter import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.metadata_writing_strategy import MetadataWritingStrategy
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestCleanupStrategy:
    def test_cleanup_strategy_wav(self):
        with temp_file_with_metadata(
            {"title": "Basic Title", "artist": "Basic Artist", "album": "Basic Album"}, "wav"
        ) as test_file:
            ID3v2MetadataSetter.set_metadata(
                test_file,
                {"title": "ID3v2 Title", "artist": "ID3v2 Artist", "album": "ID3v2 Album"},
                version="2.3",
            )

            metadata = {
                UnifiedMetadataKey.TITLE: "RIFF Title",
                UnifiedMetadataKey.ARTISTS: ["RIFF Artist"],
                UnifiedMetadataKey.ALBUM: "RIFF Album",
            }
            update_metadata(test_file, metadata, metadata_strategy=MetadataWritingStrategy.CLEANUP)

            # Verify ID3v2 was removed
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None

            # Verify RIFF has new metadata
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "RIFF Title"

            # Merged metadata should only have RIFF (ID3v2 was cleaned up)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "RIFF Title"

    def test_cleanup_strategy_mp3_id3v1_not_preserved(self):
        # Create test file with ID3v1 metadata using external script
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Add ID3v1 metadata using temp_file_with_metadata
            ID3v1MetadataSetter.set_metadata(
                test_file, {"title": "ID3v1 Title", "artist": "ID3v1 Artist", "album": "ID3v1 Album"}
            )

            # Verify ID3v1 metadata was written
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Now write ID3v2 metadata with CLEANUP strategy
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v2 Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v2 Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v2 Album",
            }
            update_metadata(test_file, id3v2_metadata, metadata_strategy=MetadataWritingStrategy.CLEANUP)

            # Verify ID3v1 metadata behavior with CLEANUP strategy
            # ID3v1 should be removed (cleaned up) with CLEANUP strategy
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None  # ID3v1 was cleaned up

            # Verify ID3v2 metadata was written
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Merged metadata should prefer ID3v2 (higher precedence)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"
