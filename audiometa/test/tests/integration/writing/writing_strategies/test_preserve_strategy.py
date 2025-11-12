"""Tests for PRESERVE metadata writing strategy.

This module tests the PRESERVE strategy which writes to native format only and preserves existing metadata in other
formats.
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
class TestPreserveStrategy:
    def test_preserve_strategy_wav(self):
        with temp_file_with_metadata(
            {"title": "ID3v2 Title", "artist": "ID3v2 Artist", "album": "ID3v2 Album"}, "wav"
        ) as test_file:
            ID3v2MetadataSetter.set_metadata(
                test_file,
                {"title": "ID3v2 Title", "artist": "ID3v2 Artist", "album": "ID3v2 Album"},
                version="2.3",
            )

            # Verify ID3v2 metadata was written
            id3v2_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_result.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Now write RIFF metadata with PRESERVE strategy (default)
            # This part still uses the app's function since we're testing the strategy
            riff_metadata = {
                UnifiedMetadataKey.TITLE: "RIFF Title",
                UnifiedMetadataKey.ARTISTS: ["RIFF Artist"],
                UnifiedMetadataKey.ALBUM: "RIFF Album",
            }
            update_metadata(test_file, riff_metadata, metadata_strategy=MetadataWritingStrategy.PRESERVE)

            # Merged metadata should prefer RIFF (WAV native format has higher precedence)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "RIFF Title"

    def test_preserve_strategy_mp3_id3v1_not_preserved(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v1MetadataSetter.set_metadata(
                test_file, {"title": "ID3v1 Title", "artist": "ID3v1 Artist", "album": "ID3v1 Album"}
            )

            # Verify ID3v1 metadata was written
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Now write ID3v2 metadata with PRESERVE strategy
            metadata = {
                UnifiedMetadataKey.TITLE: "ID3v2 Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v2 Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v2 Album",
            }
            update_metadata(test_file, metadata, metadata_strategy=MetadataWritingStrategy.PRESERVE)

            # Verify ID3v1 metadata behavior with PRESERVE strategy
            # ID3v1 should be preserved (not overwritten) with PRESERVE strategy
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"  # ID3v1 was preserved

            # Verify ID3v2 metadata was written
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Merged metadata should prefer ID3v2 (higher precedence)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"
