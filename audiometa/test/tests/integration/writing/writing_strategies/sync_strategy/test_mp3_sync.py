"""Tests for SYNC metadata writing strategy on MP3 files.

This module tests the SYNC strategy which writes to native format (ID3v2) and synchronizes other metadata formats
that are already present (ID3v1).
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
class TestMp3SyncStrategy:
    def test_mp3_no_metadata_sync(self):
        """Test SYNC strategy on MP3 file with no existing metadata.

        SYNC should write to ID3v2 (native) but NOT create ID3v1.
        """
        with temp_file_with_metadata({}, "mp3") as test_file:
            # File starts with no metadata
            mp3_metadata = {
                UnifiedMetadataKey.TITLE: "MP3 Title",
                UnifiedMetadataKey.ARTISTS: ["MP3 Artist"],
                UnifiedMetadataKey.ALBUM: "MP3 Album",
            }
            update_metadata(test_file, mp3_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify ID3v2 metadata was written
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "MP3 Title"
            assert id3v2_after.get(UnifiedMetadataKey.ARTISTS) == ["MP3 Artist"]
            assert id3v2_after.get(UnifiedMetadataKey.ALBUM) == "MP3 Album"

            # Verify ID3v1 was NOT created
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None
            assert id3v1_after.get(UnifiedMetadataKey.ARTISTS) is None
            assert id3v1_after.get(UnifiedMetadataKey.ALBUM) is None

            # Merged metadata should show ID3v2 values
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "MP3 Title"

    def test_mp3_id3v1_only_sync(self):
        """Test SYNC strategy on MP3 file with only ID3v1 metadata.

        SYNC should write to ID3v2 (native) and sync to ID3v1 (existing).
        """
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Add ID3v1 metadata using external tools
            ID3v1MetadataSetter.set_metadata(
                test_file, {"title": "ID3v1 Title", "artist": "ID3v1 Artist", "album": "ID3v1 Album"}
            )

            # Verify ID3v1 metadata was written
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Now write ID3v2 metadata with SYNC strategy
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, id3v2_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify ID3v1 metadata was synced (overwritten)
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 metadata was written
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Merged metadata should prefer ID3v2 (higher precedence)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_mp3_id3v2_only_sync(self):
        """Test SYNC strategy on MP3 file with only ID3v2 metadata.

        SYNC should write to ID3v2 (native) but NOT create ID3v1.
        """
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Add ID3v2 metadata using external tools
            ID3v2MetadataSetter.set_metadata(
                test_file,
                {"title": "ID3v2 Title", "artist": "ID3v2 Artist", "album": "ID3v2 Album"},
                version="2.3",
            )

            # Verify ID3v2 metadata was written
            id3v2_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_result.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Now write ID3v2 metadata with SYNC strategy
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "Updated Title",
                UnifiedMetadataKey.ARTISTS: ["Updated Artist"],
                UnifiedMetadataKey.ALBUM: "Updated Album",
            }
            update_metadata(test_file, id3v2_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify ID3v2 metadata was updated
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Updated Title"

            # Verify ID3v1 was NOT created
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should show updated ID3v2 values
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Updated Title"

    def test_mp3_both_formats_sync(self):
        """Test SYNC strategy on MP3 file with both ID3v1 and ID3v2 metadata.

        SYNC should write to ID3v2 (native) and sync to ID3v1 (existing).
        """
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Add ID3v1 metadata using external tools
            ID3v1MetadataSetter.set_metadata(
                test_file, {"title": "ID3v1 Title", "artist": "ID3v1 Artist", "album": "ID3v1 Album"}
            )

            # Add ID3v2 metadata using external tools
            ID3v2MetadataSetter.set_metadata(
                test_file,
                {"title": "ID3v2 Title", "artist": "ID3v2 Artist", "album": "ID3v2 Album"},
                version="2.3",
            )

            # Verify both formats have metadata
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            id3v2_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_result.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Now write ID3v2 metadata with SYNC strategy
            sync_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
                UnifiedMetadataKey.GENRES_NAMES: ["Jazz", "Blues"],
                UnifiedMetadataKey.ALBUM_ARTISTS: ["Album Artist 1", "Album Artist 2"],
            }
            update_metadata(test_file, sync_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify ID3v2 metadata has all values
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"
            assert id3v2_after.get(UnifiedMetadataKey.GENRES_NAMES) == ["Jazz", "Blues"]
            assert id3v2_after.get(UnifiedMetadataKey.ALBUM_ARTISTS) == ["Album Artist 1", "Album Artist 2"]

            # Verify ID3v1 metadata was synced with supported fields only
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"
            assert id3v1_after.get(UnifiedMetadataKey.ARTISTS) == ["Synced Artist"]
            assert id3v1_after.get(UnifiedMetadataKey.ALBUM) == "Synced Album"
            assert id3v1_after.get(UnifiedMetadataKey.GENRES_NAMES) == ["Jazz"]  # Only first genre in ID3v1
            assert id3v1_after.get(UnifiedMetadataKey.ALBUM_ARTISTS) is None  # Not supported

            # Merged metadata should prefer ID3v2
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"
            assert merged.get(UnifiedMetadataKey.GENRES_NAMES) == ["Jazz", "Blues"]
            assert merged.get(UnifiedMetadataKey.ALBUM_ARTISTS) == ["Album Artist 1", "Album Artist 2"]
