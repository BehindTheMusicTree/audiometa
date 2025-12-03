"""Tests for SYNC metadata writing strategy on WAV files.

This module tests the SYNC strategy which writes to native format (RIFF) and synchronizes other metadata formats
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
class TestWavSyncStrategy:
    def test_wav_no_metadata_sync(self):
        """Test SYNC strategy on WAV file with no existing metadata.

        SYNC should write to RIFF (native) but NOT create ID3v1 or ID3v2.
        """
        with temp_file_with_metadata({}, "wav") as test_file:
            # File starts with no metadata
            wav_metadata = {
                UnifiedMetadataKey.TITLE: "WAV Title",
                UnifiedMetadataKey.ARTISTS: ["WAV Artist"],
                UnifiedMetadataKey.ALBUM: "WAV Album",
            }
            update_metadata(test_file, wav_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify RIFF metadata was written
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "WAV Title"
            assert riff_after.get(UnifiedMetadataKey.ARTISTS) == ["WAV Artist"]
            assert riff_after.get(UnifiedMetadataKey.ALBUM) == "WAV Album"

            # Verify ID3v1 was NOT created
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

            # Verify ID3v2 was NOT created
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should show RIFF values
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "WAV Title"

    def test_wav_riff_only_sync(self):
        """Test SYNC strategy on WAV file with only RIFF metadata.

        SYNC should write to RIFF (native) but NOT create ID3v1 or ID3v2.
        """
        with temp_file_with_metadata(
            {"title": "Initial Title", "artist": "Initial Artist", "album": "Initial Album"}, "wav"
        ) as test_file:
            # File has RIFF metadata
            riff_initial = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_initial.get(UnifiedMetadataKey.TITLE) == "Initial Title"

            # Now write RIFF metadata with SYNC strategy
            riff_metadata = {
                UnifiedMetadataKey.TITLE: "Updated Title",
                UnifiedMetadataKey.ARTISTS: ["Updated Artist"],
                UnifiedMetadataKey.ALBUM: "Updated Album",
            }
            update_metadata(test_file, riff_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify RIFF metadata was updated
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "Updated Title"

            # Verify ID3v1 was NOT created
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

            # Verify ID3v2 was NOT created
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should show updated RIFF values
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Updated Title"

    def test_wav_id3v1_only_sync(self):
        """Test SYNC strategy on WAV file with only ID3v1 metadata.

        SYNC should write to RIFF (native) and sync to ID3v1 (existing).
        """
        with temp_file_with_metadata({}, "wav") as test_file:
            # Add ID3v1 metadata using external tools
            ID3v1MetadataSetter.set_metadata(
                test_file, {"title": "ID3v1 Title", "artist": "ID3v1 Artist", "album": "ID3v1 Album"}
            )

            # Verify ID3v1 metadata was written
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Now write RIFF metadata with SYNC strategy
            riff_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, riff_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify RIFF metadata was written
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v1 metadata was synced (overwritten)
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 was NOT created
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should prefer RIFF (higher precedence)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_wav_id3v2_only_sync(self):
        """Test SYNC strategy on WAV file with only ID3v2 metadata.

        SYNC should write to RIFF (native) and sync to ID3v2 (existing).
        """
        with temp_file_with_metadata({}, "wav") as test_file:
            # Add ID3v2 metadata using external tools
            ID3v2MetadataSetter.set_metadata(
                test_file,
                {"title": "ID3v2 Title", "artist": "ID3v2 Artist", "album": "ID3v2 Album"},
                version="2.3",
            )

            # Verify ID3v2 metadata was written
            id3v2_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_result.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Now write RIFF metadata with SYNC strategy
            riff_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, riff_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify RIFF metadata was written
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 metadata was synced (overwritten)
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v1 was NOT created
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should prefer RIFF (higher precedence)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_wav_riff_plus_id3v1_sync(self):
        """Test SYNC strategy on WAV file with RIFF and ID3v1 metadata.

        SYNC should write to RIFF (native) and sync to ID3v1 (existing).
        """
        with temp_file_with_metadata(
            {"title": "RIFF Title", "artist": "RIFF Artist", "album": "RIFF Album"}, "wav"
        ) as test_file:
            # Add ID3v1 metadata using external tools
            ID3v1MetadataSetter.set_metadata(
                test_file, {"title": "ID3v1 Title", "artist": "ID3v1 Artist", "album": "ID3v1 Album"}
            )

            # Verify both formats have metadata
            riff_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_result.get(UnifiedMetadataKey.TITLE) == "RIFF Title"
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Now write RIFF metadata with SYNC strategy
            sync_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, sync_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify RIFF metadata was updated
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v1 metadata was synced
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 was NOT created
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should prefer RIFF
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_wav_riff_plus_id3v2_sync(self):
        """Test SYNC strategy on WAV file with RIFF and ID3v2 metadata.

        SYNC should write to RIFF (native) and sync to ID3v2 (existing).
        """
        with temp_file_with_metadata(
            {"title": "RIFF Title", "artist": "RIFF Artist", "album": "RIFF Album"}, "wav"
        ) as test_file:
            # Add ID3v2 metadata using external tools
            ID3v2MetadataSetter.set_metadata(
                test_file,
                {"title": "ID3v2 Title", "artist": "ID3v2 Artist", "album": "ID3v2 Album"},
                version="2.3",
            )

            # Verify both formats have metadata
            riff_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_result.get(UnifiedMetadataKey.TITLE) == "RIFF Title"
            id3v2_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_result.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Now write RIFF metadata with SYNC strategy
            sync_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, sync_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify RIFF metadata was updated
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 metadata was synced
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v1 was NOT created
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

            # Merged metadata should prefer RIFF
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_wav_all_formats_sync(self):
        """Test SYNC strategy on WAV file with RIFF, ID3v1, and ID3v2 metadata.

        SYNC should write to RIFF (native) and sync to ID3v1 and ID3v2 (existing).
        """
        with temp_file_with_metadata(
            {"title": "RIFF Title", "artist": "RIFF Artist", "album": "RIFF Album"}, "wav"
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
            riff_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_result.get(UnifiedMetadataKey.TITLE) == "RIFF Title"
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            id3v2_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_result.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Now write RIFF metadata with SYNC strategy
            sync_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, sync_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify RIFF metadata was updated
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v1 metadata was synced
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Verify ID3v2 metadata was synced
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Merged metadata should prefer RIFF
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"
