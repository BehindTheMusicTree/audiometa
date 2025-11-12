"""Tests for SYNC metadata writing strategy.

This module tests the SYNC strategy which writes to native format and synchronizes other metadata formats that are
already present.
"""

import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.test.helpers.id3v1.id3v1_metadata_setter import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.metadata_writing_strategy import MetadataWritingStrategy
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestSyncStrategy:
    def test_sync_strategy_wav(self):
        # Create WAV file with initial RIFF metadata
        with temp_file_with_metadata(
            {"title": "Initial Title", "artist": "Initial Artist", "album": "Initial Album"}, "wav"
        ) as test_file:
            # Verify initial RIFF metadata was written
            riff_initial = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_initial.get(UnifiedMetadataKey.TITLE) == "Initial Title"

            # Now write RIFF metadata with SYNC strategy
            # For WAV files, SYNC strategy should only affect RIFF metadata
            sync_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, sync_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify RIFF metadata has the synced values
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"
            assert riff_after.get(UnifiedMetadataKey.ARTISTS) == ["Synced Artist"]
            assert riff_after.get(UnifiedMetadataKey.ALBUM) == "Synced Album"

            # Verify merged metadata prefers RIFF (WAV native format)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_default_strategy_is_sync(self):
        # Create WAV file with initial RIFF metadata
        with temp_file_with_metadata({}, "wav") as test_file:
            # First, add RIFF metadata using external tools
            RIFFMetadataSetter.set_title(test_file, "Initial RIFF Title")
            RIFFMetadataSetter.set_artists(test_file, ["Initial RIFF Artist"])

            # Now write RIFF metadata without specifying strategy (should default to SYNC)
            riff_metadata = {UnifiedMetadataKey.TITLE: "RIFF Title", UnifiedMetadataKey.ARTISTS: ["RIFF Artist"]}
            update_metadata(test_file, riff_metadata)

            # Verify RIFF metadata has the new values (SYNC strategy)
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "RIFF Title"

            # Merged metadata should prefer RIFF (WAV native format)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "RIFF Title"

    def test_id3v1_not_preserved_with_sync_strategy(self):
        # Create test file with ID3v1 metadata using external tools
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

            # Verify ID3v1 metadata behavior with different strategies
            # When ID3v2 is written, it overwrites the ID3v1 tag
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"  # ID3v1 was overwritten

            # Verify ID3v2 metadata was written with synced values
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            # Merged metadata should prefer ID3v2 (higher precedence)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_id3v1_modification_success(self):
        # Create test file with ID3v1 metadata using external tools
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Add ID3v1 metadata using external tools
            ID3v1MetadataSetter.set_metadata(
                test_file, {"title": "ID3v1 Title", "artist": "ID3v1 Artist", "album": "ID3v1 Album"}
            )

            # Verify ID3v1 metadata was written
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Modify ID3v1 metadata directly should succeed
            update_metadata(test_file, {UnifiedMetadataKey.TITLE: "New Title"}, metadata_format=MetadataFormat.ID3V1)

            # Verify the modification was successful
            updated_id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert updated_id3v1_result.get(UnifiedMetadataKey.TITLE) == "New Title"

    def test_sync_strategy_wav_with_field_length_limits(self):
        # Create WAV file with initial RIFF metadata
        with temp_file_with_metadata({}, "wav") as test_file:
            # Add initial RIFF metadata using external tools
            RIFFMetadataSetter.set_title(test_file, "Short Title")
            RIFFMetadataSetter.set_artists(test_file, ["Short Artist"])
            RIFFMetadataSetter.set_album(test_file, "Short Album")

            # Verify initial RIFF metadata was written
            riff_initial = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_initial.get(UnifiedMetadataKey.TITLE) == "Short Title"

            # Now test SYNC strategy with long title
            long_title = "This is a Very Long Title That Tests RIFF Metadata Handling"
            sync_metadata = {
                UnifiedMetadataKey.TITLE: long_title,
                UnifiedMetadataKey.ARTISTS: ["Long Artist Name That Tests RIFF Handling"],
                UnifiedMetadataKey.ALBUM: "Long Album Name That Tests RIFF Handling",
            }
            update_metadata(test_file, sync_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify RIFF metadata has full values (RIFF supports longer fields than ID3v1)
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == long_title
            assert riff_after.get(UnifiedMetadataKey.ARTISTS) == ["Long Artist Name That Tests RIFF Handling"]
            assert riff_after.get(UnifiedMetadataKey.ALBUM) == "Long Album Name That Tests RIFF Handling"

            # Merged metadata should prefer RIFF (WAV native format has higher precedence)
            merged = get_unified_metadata(test_file)
            assert merged.get(UnifiedMetadataKey.TITLE) == long_title  # Full title from RIFF
            assert merged.get(UnifiedMetadataKey.ARTISTS) == ["Long Artist Name That Tests RIFF Handling"]

    def test_sync_strategy_mp3(self):
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

            # Verify ID3v1 metadata behavior with different strategies
            # When ID3v2 is written, it overwrites the ID3v1 tag
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"  # ID3v1 was overwritten

            # Verify ID3v2 metadata was written with synced values
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

    def test_sync_strategy_flac(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ID3v1MetadataSetter.set_metadata(
                test_file, {"title": "ID3v1 Title", "artist": "ID3v1 Artist", "album": "ID3v1 Album"}
            )

            # Verify ID3v1 metadata was written
            id3v1_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_result.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            ID3v2MetadataSetter.set_metadata(
                test_file,
                {"title": "ID3v2 Title", "artist": "ID3v2 Artist", "album": "ID3v2 Album"},
                version="2.3",
            )
            id3v2_result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_result.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Now write Vorbis metadata with SYNC strategy
            vorbis_metadata = {
                UnifiedMetadataKey.TITLE: "Synced Title",
                UnifiedMetadataKey.ARTISTS: ["Synced Artist"],
                UnifiedMetadataKey.ALBUM: "Synced Album",
            }
            update_metadata(test_file, vorbis_metadata, metadata_strategy=MetadataWritingStrategy.SYNC)

            # Verify ID3v1 metadata behavior with different strategies
            # When Vorbis is written, it overwrites the ID3v1 tag
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"  # ID3v1 was overwritten

            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"

            vorbis_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert vorbis_after.get(UnifiedMetadataKey.TITLE) == "Synced Title"
