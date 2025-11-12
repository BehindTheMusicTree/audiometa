"""Tests for multiple format preservation when updating metadata.

This module tests that updating fields in one format with the PRESERVE strategy does not affect other formats. It covers
the main working combinations.
"""

import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestMultipleFormatPreservation:
    def test_id3v1_preserves_id3v2(self):
        with temp_file_with_metadata({"title": "ID3v2 Title", "artist": "ID3v2 Artist"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            ID3v2MetadataSetter.set_metadata(test_file, {"artist": "ID3v2 Artist"})

            # Verify initial state
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            id3v1_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"
            assert id3v1_before.get(UnifiedMetadataKey.TITLE) is None

            # Update ID3v1 with PRESERVE strategy (specify ID3v1 format)
            id3v1_metadata = {UnifiedMetadataKey.TITLE: "ID3v1 Title", UnifiedMetadataKey.ARTISTS: ["ID3v1 Artist"]}
            update_metadata(test_file, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            # Verify ID3v1 was updated and ID3v2 was preserved
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

    def test_id3v2_preserves_id3v1(self):
        with temp_file_with_metadata({"title": "ID3v1 Title", "artist": "ID3v1 Artist"}, "id3v1") as test_file:
            # Verify initial state
            id3v1_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v1_before.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) is None

            id3v2_metadata = {UnifiedMetadataKey.TITLE: "ID3v2 Title", UnifiedMetadataKey.ARTISTS: ["ID3v2 Artist"]}
            update_metadata(test_file, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            # Verify ID3v2 was updated and ID3v1 was preserved
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

    def test_riff_preserves_id3v1(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v1MetadataSetter.set_artist(test_file, "ID3v1 Artist")

            # Verify initial state
            id3v1_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            riff_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert id3v1_before.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            assert riff_before.get(UnifiedMetadataKey.TITLE) is None

            riff_metadata = {UnifiedMetadataKey.TITLE: "RIFF Title", UnifiedMetadataKey.ARTISTS: ["RIFF Artist"]}
            update_metadata(test_file, riff_metadata, metadata_format=MetadataFormat.RIFF)

            # Verify RIFF was updated and ID3v1 was preserved
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "RIFF Title"

    def test_id3v1_preserves_riff(self):
        with temp_file_with_metadata({"title": "RIFF Title", "artist": "RIFF Artist"}, "wav") as test_file:
            # Verify initial state
            riff_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            id3v1_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert riff_before.get(UnifiedMetadataKey.TITLE) == "RIFF Title"
            assert id3v1_before.get(UnifiedMetadataKey.TITLE) is None

            # Update ID3v1 with PRESERVE strategy (specify ID3v1 format)
            id3v1_metadata = {UnifiedMetadataKey.TITLE: "ID3v1 Title", UnifiedMetadataKey.ARTISTS: ["ID3v1 Artist"]}
            update_metadata(test_file, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            # Verify ID3v1 was updated and RIFF was preserved
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "RIFF Title"
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

    def test_riff_preserves_id3v2(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            ID3v2MetadataSetter.set_metadata(test_file, {"artist": "ID3v2 Artist"})

            # Verify initial state
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            riff_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"
            assert riff_before.get(UnifiedMetadataKey.TITLE) is None

            # Update RIFF with PRESERVE strategy (specify RIFF format)
            riff_metadata = {UnifiedMetadataKey.TITLE: "RIFF Title", UnifiedMetadataKey.ARTISTS: ["RIFF Artist"]}
            update_metadata(test_file, riff_metadata, metadata_format=MetadataFormat.RIFF)

            # Verify RIFF was updated and ID3v2 was preserved
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "RIFF Title"

    def test_id3v2_preserves_riff(self):
        with temp_file_with_metadata({"title": "RIFF Title", "artist": "RIFF Artist"}, "wav") as test_file:
            # Verify initial state
            riff_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert riff_before.get(UnifiedMetadataKey.TITLE) == "RIFF Title"
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) is None

            # Update ID3v2 with PRESERVE strategy (specify ID3v2 format)
            id3v2_metadata = {UnifiedMetadataKey.TITLE: "ID3v2 Title", UnifiedMetadataKey.ARTISTS: ["ID3v2 Artist"]}
            update_metadata(test_file, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            # Verify ID3v2 was updated and RIFF was preserved
            riff_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert riff_after.get(UnifiedMetadataKey.TITLE) == "RIFF Title"
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

    def test_vorbis_preserves_id3v2(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"})
            ID3v2MetadataSetter.set_metadata(test_file, {"artist": "ID3v2 Artist"})

            # Verify initial state
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            vorbis_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"
            assert vorbis_before.get(UnifiedMetadataKey.TITLE) is None

            # Update Vorbis with PRESERVE strategy (specify Vorbis format)
            vorbis_metadata = {UnifiedMetadataKey.TITLE: "Vorbis Title", UnifiedMetadataKey.ARTISTS: ["Vorbis Artist"]}
            update_metadata(test_file, vorbis_metadata, metadata_format=MetadataFormat.VORBIS)

            # Verify Vorbis was updated and ID3v2 was preserved
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            vorbis_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"
            assert vorbis_after.get(UnifiedMetadataKey.TITLE) == "Vorbis Title"

    def test_id3v2_preserves_vorbis(self):
        with temp_file_with_metadata({"title": "Vorbis Title", "artist": "Vorbis Artist"}, "flac") as test_file:
            # Verify initial state
            vorbis_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert vorbis_before.get(UnifiedMetadataKey.TITLE) == "Vorbis Title"
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) is None

            # Update ID3v2 with PRESERVE strategy (specify ID3v2 format)
            id3v2_metadata = {UnifiedMetadataKey.TITLE: "ID3v2 Title", UnifiedMetadataKey.ARTISTS: ["ID3v2 Artist"]}
            update_metadata(test_file, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            # Verify ID3v2 was updated and Vorbis was preserved
            vorbis_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert vorbis_after.get(UnifiedMetadataKey.TITLE) == "Vorbis Title"
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

    def test_multiple_fields_preservation(self):
        with temp_file_with_metadata({"title": "Original Title", "artist": "Original Artist"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v1MetadataSetter.set_artist(test_file, "ID3v1 Artist")
            # Use ID3v2.3 instead of ID3v2.4 to preserve ID3v1 metadata
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title"}, version="2.3")
            ID3v2MetadataSetter.set_metadata(test_file, {"artist": "ID3v2 Artist"}, version="2.3")

            # Verify initial state
            id3v1_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v1_before.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Update only ID3v2 with multiple fields
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "Updated ID3v2 Title",
                UnifiedMetadataKey.ARTISTS: ["Updated ID3v2 Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v2 Album",
            }
            update_metadata(test_file, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            # Verify ID3v2 was updated and ID3v1 was preserved
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            assert id3v1_after.get(UnifiedMetadataKey.ARTISTS) == ["ID3v1 Artist"]
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) == "Updated ID3v2 Title"
            assert id3v2_after.get(UnifiedMetadataKey.ARTISTS) == ["Updated ID3v2 Artist"]
            assert id3v2_after.get(UnifiedMetadataKey.ALBUM) == "ID3v2 Album"

    def test_preserve_strategy_with_none_values(self):
        with temp_file_with_metadata({"title": "Original Title", "artist": "Original Artist"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v1MetadataSetter.set_artist(test_file, "ID3v1 Artist")

            # Verify initial state
            id3v1_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_before.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Update ID3v2 with None values (should not affect ID3v1)
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: None,  # This should not affect ID3v1
                UnifiedMetadataKey.ARTISTS: ["ID3v2 Artist"],
            }
            update_metadata(test_file, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            # Verify ID3v1 was preserved
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            assert id3v1_after.get(UnifiedMetadataKey.ARTISTS) == ["ID3v1 Artist"]
