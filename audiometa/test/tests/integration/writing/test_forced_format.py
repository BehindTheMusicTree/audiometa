"""Tests for forced format parameter functionality.

This module tests the behavior when a specific metadata format is forced using the metadata_format parameter in
update_metadata.
"""

import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.exceptions import (
    MetadataFieldNotSupportedByMetadataFormatError,
    MetadataFormatNotSupportedByAudioFormatError,
    MetadataWritingConflictParametersError,
)
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.metadata_writing_strategy import MetadataWritingStrategy
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestForcedFormat:
    def test_forced_format_writes_only_to_specified_format(self):
        # Create WAV file with initial RIFF metadata
        initial_metadata = {"title": "Original RIFF Title", "artist": "Original RIFF Artist"}
        with temp_file_with_metadata(initial_metadata, "wav") as test_file:
            # Add ID3v2 metadata using the library directly
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "Original ID3v2 Title",
                UnifiedMetadataKey.ARTISTS: ["Original ID3v2 Artist"],
            }
            update_metadata(test_file, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            # Verify both formats have their respective metadata
            riff_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert riff_before.get(UnifiedMetadataKey.TITLE) == "Original RIFF Title"
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) == "Original ID3v2 Title"

            # Force ID3v2 format (should write only to ID3v2, leave RIFF untouched)
            new_metadata = {
                UnifiedMetadataKey.TITLE: "New ID3v2 Title",
                UnifiedMetadataKey.ARTISTS: ["New ID3v2 Artist"],
            }

            # This should write only to ID3v2 format, leaving RIFF unchanged
            update_metadata(test_file, new_metadata, metadata_format=MetadataFormat.ID3V2)

            # Verify ID3v2 has new metadata
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "New ID3v2 Title"
            assert id3v2_after.get(UnifiedMetadataKey.ARTISTS) == ["New ID3v2 Artist"]

            # Verify RIFF still has original metadata (forced format doesn't affect other formats)
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "Original RIFF Title"
            assert riff_after.get(UnifiedMetadataKey.ARTISTS) == ["Original RIFF Artist"]

    def test_forced_format_fails_fast_on_unsupported_fields(self):
        # Create WAV file with basic metadata
        initial_metadata = {"title": "Test Title", "artist": "Test Artist"}
        with temp_file_with_metadata(initial_metadata, "wav") as test_file:
            # Try to write ARCHIVAL_LOCATION to RIFF format (not supported)
            unsupported_metadata = {
                UnifiedMetadataKey.TITLE: "Test Title",
                UnifiedMetadataKey.ARCHIVAL_LOCATION: "some location",  # ARCHIVAL_LOCATION not supported by RIFF format
            }

            # This should raise MetadataFieldNotSupportedByMetadataFormatError because format is forced
            with pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.ARCHIVAL_LOCATION metadata not supported by RIFF format",
            ):
                update_metadata(test_file, unsupported_metadata, metadata_format=MetadataFormat.RIFF)

    def test_forced_format_succeeds_with_supported_fields(self):
        # Create WAV file with basic metadata
        initial_metadata = {"title": "Test Title", "artist": "Test Artist"}
        with temp_file_with_metadata(initial_metadata, "wav") as test_file:
            # Write supported fields to RIFF format
            supported_metadata = {
                UnifiedMetadataKey.TITLE: "New RIFF Title",
                UnifiedMetadataKey.ARTISTS: ["New RIFF Artist"],
                UnifiedMetadataKey.ALBUM: "New RIFF Album",
            }

            # This should succeed because all fields are supported by RIFF
            update_metadata(test_file, supported_metadata, metadata_format=MetadataFormat.RIFF)

            # Verify RIFF has new metadata
            riff_metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_metadata.get(UnifiedMetadataKey.TITLE) == "New RIFF Title"
            assert riff_metadata.get(UnifiedMetadataKey.ARTISTS) == ["New RIFF Artist"]
            assert riff_metadata.get(UnifiedMetadataKey.ALBUM) == "New RIFF Album"

    def test_forced_format_parameter_conflict_error(self):
        # Create WAV file with basic metadata
        initial_metadata = {"title": "Test Title", "artist": "Test Artist"}
        with temp_file_with_metadata(initial_metadata, "wav") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title", UnifiedMetadataKey.ARTISTS: ["Test Artist"]}

            # This should raise error because both parameters are specified
            with pytest.raises(
                MetadataWritingConflictParametersError,
                match="Cannot specify both metadata_strategy and metadata_format",
            ):
                update_metadata(
                    test_file,
                    metadata,
                    metadata_format=MetadataFormat.RIFF,
                    metadata_strategy=MetadataWritingStrategy.SYNC,
                )

    def test_forced_format_with_unsupported_file_type(self):
        # Create MP3 file
        initial_metadata = {"title": "Test Title", "artist": "Test Artist"}
        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title", UnifiedMetadataKey.ARTISTS: ["Test Artist"]}

            # Try to force Vorbis format on MP3 file (not supported)
            with pytest.raises(
                MetadataFormatNotSupportedByAudioFormatError,
                match="Tag format MetadataFormat.VORBIS not supported for file extension .mp3",
            ):
                update_metadata(test_file, metadata, metadata_format=MetadataFormat.VORBIS)

    def test_forced_format_id3v1_writing_support(self):
        # Create MP3 file with basic metadata
        initial_metadata = {"title": "Test Title", "artist": "Test Artist"}
        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "New ID3v1 Title", UnifiedMetadataKey.ARTISTS: ["New ID3v1 Artist"]}

            update_metadata(test_file, metadata, metadata_format=MetadataFormat.ID3V1)

            # Verify the metadata was written
            from audiometa import get_unified_metadata

            result = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert result.get(UnifiedMetadataKey.TITLE) == "New ID3v1 Title"
            assert result.get(UnifiedMetadataKey.ARTISTS) == ["New ID3v1 Artist"]

    def test_forced_format_multiple_formats_present(self):
        # Create WAV file with both RIFF and ID3v2 metadata
        initial_metadata = {"title": "Original RIFF Title", "artist": "Original RIFF Artist"}
        with temp_file_with_metadata(initial_metadata, "wav") as test_file:
            # Add ID3v2 metadata using the library directly
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "Original ID3v2 Title",
                UnifiedMetadataKey.ARTISTS: ["Original ID3v2 Artist"],
            }
            update_metadata(test_file, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            # Verify both formats have original metadata
            riff_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert riff_before.get(UnifiedMetadataKey.TITLE) == "Original RIFF Title"
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) == "Original ID3v2 Title"

            # Force ID3v2 format - should only update ID3v2
            new_metadata = {
                UnifiedMetadataKey.TITLE: "New ID3v2 Title",
                UnifiedMetadataKey.ARTISTS: ["New ID3v2 Artist"],
            }

            update_metadata(test_file, new_metadata, metadata_format=MetadataFormat.ID3V2)

            # Verify ID3v2 was updated
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "New ID3v2 Title"
            assert id3v2_after.get(UnifiedMetadataKey.ARTISTS) == ["New ID3v2 Artist"]

            # Verify RIFF was NOT updated (forced format only affects specified format)
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "Original RIFF Title"
            assert riff_after.get(UnifiedMetadataKey.ARTISTS) == ["Original RIFF Artist"]

    def test_forced_format_with_rating_field(self):
        # Create MP3 file with basic metadata
        initial_metadata = {"title": "Test Title", "artist": "Test Artist"}
        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # Write rating to ID3v2 format with proper configuration
            metadata_with_rating = {UnifiedMetadataKey.TITLE: "Test Title", UnifiedMetadataKey.RATING: 80}

            # This should succeed with proper configuration
            update_metadata(
                test_file,
                metadata_with_rating,
                metadata_format=MetadataFormat.ID3V2,
                normalized_rating_max_value=100,
            )

            # Verify rating was written (converted from 0-100 to 0-255 scale)
            id3v2_metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_metadata.get(UnifiedMetadataKey.TITLE) == "Test Title"
            # Rating 85 on 0-100 scale becomes 196 on 0-255 scale (85 * 255 / 100 = 216.75, rounded to 196)
            assert id3v2_metadata.get(UnifiedMetadataKey.RATING) == 196

    # Note: delete_all_metadata tests have been moved to test_delete_all_metadata.py

    def test_forced_format_validation_before_writing(self):
        # Create WAV file with initial metadata
        initial_metadata = {"title": "Original Title", "artist": "Original Artist"}
        with temp_file_with_metadata(initial_metadata, "wav") as test_file:
            # Try to write mixed supported/unsupported fields to RIFF format
            mixed_metadata = {
                UnifiedMetadataKey.TITLE: "New Title",  # Supported
                UnifiedMetadataKey.ARTISTS: ["New Artist"],  # Supported
                UnifiedMetadataKey.ARCHIVAL_LOCATION: "some location",  # NOT supported by RIFF
                UnifiedMetadataKey.ALBUM: "New Album",  # Supported
            }

            # This should fail because ARCHIVAL_LOCATION is not supported by RIFF
            with pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.ARCHIVAL_LOCATION metadata not supported by RIFF format",
            ):
                update_metadata(test_file, mixed_metadata, metadata_format=MetadataFormat.RIFF)

            # Verify NO changes were made to the file (validation happens before writing)
            final_metadata = get_unified_metadata(test_file)
            assert final_metadata.get(UnifiedMetadataKey.TITLE) == "Original Title"
            assert final_metadata.get(UnifiedMetadataKey.ARTISTS) == ["Original Artist"]
            assert final_metadata.get(UnifiedMetadataKey.BPM) is None
            assert final_metadata.get(UnifiedMetadataKey.ALBUM) is None
