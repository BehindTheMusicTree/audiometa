"""Tests for SYNC metadata writing strategy on FLAC files.

This module tests the SYNC strategy which writes to native format (Vorbis) and synchronizes other metadata formats
that are already present (ID3v1, ID3v2).
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
class TestFlacSyncStrategy:
    def test_flac_no_metadata_sync(self):
        """Test SYNC strategy on FLAC file with no existing metadata.

        SYNC should write to Vorbis (native) but NOT create ID3v1 or ID3v2.
        """
        with temp_file_with_metadata({}, "flac") as test_file:
            # File starts with no metadata
            flac_metadata = {
                UnifiedMetadataKey.TITLE: "FLAC Title",
                UnifiedMetadataKey.ARTISTS: ["FLAC Artist"],
                UnifiedMetadataKey.ALBUM: "FLAC Album",
            }
            update_metadata(test_file, flac_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify Vorbis metadata was written
            vorbis_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_after.get(UnifiedMetadataKey.TITLE) == "FLAC Title"
            assert vorbis_after.get(UnifiedMetadataKey.ARTISTS) == ["FLAC Artist"]
            assert vorbis_after.get(UnifiedMetadataKey.ALBUM) == "FLAC Album"

            # Verify ID3v1 was NOT created
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

            # Verify ID3v2 was NOT created
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should show Vorbis values
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "FLAC Title"

    def test_flac_vorbis_only_sync(self):
        """Test SYNC strategy on FLAC file with only Vorbis metadata.

        SYNC should write to Vorbis (native) but NOT create ID3v1 or ID3v2.
        """
        with temp_file_with_metadata(
            {"title": "Initial Title", "artist": "Initial Artist", "album": "Initial Album"}, "flac"
        ) as test_file:
            # File has Vorbis metadata
            vorbis_initial = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_initial.get(UnifiedMetadataKey.TITLE) == "Initial Title"

            # Now write Vorbis metadata with SYNC strategy
            vorbis_metadata = {
                UnifiedMetadataKey.TITLE: "Updated Title",
                UnifiedMetadataKey.ARTISTS: ["Updated Artist"],
                UnifiedMetadataKey.ALBUM: "Updated Album",
            }
            update_metadata(test_file, vorbis_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify Vorbis metadata was updated
            vorbis_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_after.get(UnifiedMetadataKey.TITLE) == "Updated Title"

            # Verify ID3v1 was NOT created
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

            # Verify ID3v2 was NOT created
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should show updated Vorbis values
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Updated Title"

    def test_flac_id3v1_only_sync(self):
        """Test SYNC strategy on FLAC file with only ID3v1 metadata.

        SYNC should write to Vorbis (native) and sync to ID3v1 (existing).
        """
        with temp_file_with_metadata({}, "flac") as test_file:
            # Add ID3v1 metadata using external tools
            ID3v1MetadataSetter.set_metadata(
                test_file, {"title": "ID3v1 Title", "artist": "ID3v1 Artist", "album": "ID3v1 Album"}
            )

            # Verify ID3v1 metadata was written
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Now write Vorbis metadata with SYNC strategy
            vorbis_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, vorbis_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify Vorbis metadata was written
            vorbis_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v1 metadata was synced (overwritten)
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 was NOT created
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should prefer Vorbis (higher precedence)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_flac_id3v2_only_sync(self):
        """Test SYNC strategy on FLAC file with only ID3v2 metadata.

        SYNC should write to Vorbis (native) and sync to ID3v2 (existing).
        """
        with temp_file_with_metadata({}, "flac") as test_file:
            # Add ID3v2 metadata using external tools
            ID3v2MetadataSetter.set_metadata(
                test_file,
                {"title": "ID3v2 Title", "artist": "ID3v2 Artist", "album": "ID3v2 Album"},
                version="2.3",
            )

            # Verify ID3v2 metadata was written
            id3v2_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_result.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Now write Vorbis metadata with SYNC strategy
            vorbis_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, vorbis_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify Vorbis metadata was written
            vorbis_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 metadata was synced (overwritten)
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v1 was NOT created
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should prefer Vorbis (higher precedence)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_flac_vorbis_plus_id3v1_sync(self):
        """Test SYNC strategy on FLAC file with Vorbis and ID3v1 metadata.

        SYNC should write to Vorbis (native) and sync to ID3v1 (existing).
        """
        with temp_file_with_metadata(
            {"title": "Vorbis Title", "artist": "Vorbis Artist", "album": "Vorbis Album"}, "flac"
        ) as test_file:
            # Add ID3v1 metadata using external tools
            ID3v1MetadataSetter.set_metadata(
                test_file, {"title": "ID3v1 Title", "artist": "ID3v1 Artist", "album": "ID3v1 Album"}
            )

            # Verify both formats have metadata
            vorbis_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_result.get(UnifiedMetadataKey.TITLE) == "Vorbis Title"
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Now write Vorbis metadata with SYNC strategy
            sync_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, sync_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify Vorbis metadata was updated
            vorbis_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v1 metadata was synced
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 was NOT created
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should prefer Vorbis
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_flac_vorbis_plus_id3v2_sync(self):
        """Test SYNC strategy on FLAC file with Vorbis and ID3v2 metadata.

        SYNC should write to Vorbis (native) and sync to ID3v2 (existing).
        """
        with temp_file_with_metadata(
            {"title": "Vorbis Title", "artist": "Vorbis Artist", "album": "Vorbis Album"}, "flac"
        ) as test_file:
            # Add ID3v2 metadata using external tools
            ID3v2MetadataSetter.set_metadata(
                test_file,
                {"title": "ID3v2 Title", "artist": "ID3v2 Artist", "album": "ID3v2 Album"},
                version="2.3",
            )

            # Verify both formats have metadata
            vorbis_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_result.get(UnifiedMetadataKey.TITLE) == "Vorbis Title"
            id3v2_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_result.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Now write Vorbis metadata with SYNC strategy
            sync_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, sync_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify Vorbis metadata was updated
            vorbis_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 metadata was synced
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v1 was NOT created
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should prefer Vorbis
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_flac_all_formats_sync(self):
        """Test SYNC strategy on FLAC file with Vorbis, ID3v1, and ID3v2 metadata.

        SYNC should write to Vorbis (native) and sync to ID3v1 and ID3v2 (existing).
        """
        with temp_file_with_metadata(
            {"title": "Vorbis Title", "artist": "Vorbis Artist", "album": "Vorbis Album"}, "flac"
        ) as test_file:
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

            # Verify all formats have metadata
            vorbis_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_result.get(UnifiedMetadataKey.TITLE) == "Vorbis Title"
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            id3v2_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_result.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Now write Vorbis metadata with SYNC strategy
            sync_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, sync_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify Vorbis metadata was updated
            vorbis_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v1 metadata was synced
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 metadata was synced
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Merged metadata should prefer Vorbis
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"
