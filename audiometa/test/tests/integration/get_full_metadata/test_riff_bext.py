"""Integration tests for RIFF bext chunk extraction via get_full_metadata.

This file is kept separate from other format tests because bext is a sub-feature
(BWF extension) of RIFF, not a separate metadata format. It tests:

- bext-specific chunk extraction via get_full_metadata
- bext chunk structure in chunk_structure
- Consistency between manager and get_full_metadata for bext
- Edge cases specific to bext (e.g., extraction without INFO metadata)

Unlike other metadata formats (ID3v2, ID3v1, Vorbis) which are tested in general
structure/format files, bext warrants dedicated tests due to its unique integration
behavior and specific edge cases.
"""

from pathlib import Path

import pytest

from audiometa import get_full_metadata
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.integration
class TestRiffBextChunkStructure:
    """Test cases for RIFF bext chunk extraction via get_full_metadata."""

    def test_bext_chunk_structure_present_in_get_full_metadata(self):
        """Test that bext chunk appears in chunk_structure when present."""
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_bext_description(test_file, "Test Description")
            RIFFMetadataSetter.set_bext_originator(test_file, "Test Originator")

            result = get_full_metadata(test_file)

            riff_raw = result.get("raw_metadata", {}).get("riff", {})
            assert "chunk_structure" in riff_raw
            assert "bext" in riff_raw["chunk_structure"]

            bext_data = riff_raw["chunk_structure"]["bext"]
            assert bext_data["Description"] == "Test Description"
            assert bext_data["Originator"] == "Test Originator"

    def test_bext_chunk_structure_with_all_fields(self):
        """Test bext chunk extraction with all fields via get_full_metadata."""
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_bext_metadata(
                test_file,
                {
                    "Description": "Test Description",
                    "Originator": "Test Originator",
                    "OriginatorReference": "REF-12345",
                    "OriginationDate": "2024-01-15",
                    "OriginationTime": "14:30:00",
                    "TimeReference": 44100,
                    "CodingHistory": "A=PCM,F=44100,W=16,M=mono,T=PCM",
                },
            )

            result = get_full_metadata(test_file)

            riff_raw = result.get("raw_metadata", {}).get("riff", {})
            assert "chunk_structure" in riff_raw
            assert "bext" in riff_raw["chunk_structure"]

            bext_data = riff_raw["chunk_structure"]["bext"]
            assert bext_data["Description"] == "Test Description"
            assert bext_data["Originator"] == "Test Originator"
            assert bext_data["OriginatorReference"] == "REF-12345"
            assert bext_data["OriginationDate"] == "2024-01-15"
            assert bext_data["OriginationTime"] == "14:30:00"
            assert bext_data["TimeReference"] == 44100
            assert bext_data["CodingHistory"] == "A=PCM,F=44100,W=16,M=mono,T=PCM"

    def test_bext_chunk_structure_absent_when_not_present(self, sample_wav_file: Path):
        """Test that bext chunk is not present in chunk_structure for regular WAV files."""
        result = get_full_metadata(sample_wav_file)

        riff_raw = result.get("raw_metadata", {}).get("riff", {})
        assert "chunk_structure" in riff_raw
        # Regular WAV files without bext chunk should not have bext in chunk_structure
        assert "bext" not in riff_raw["chunk_structure"]

    def test_bext_chunk_structure_consistency_with_manager(self):
        """Test that get_full_metadata returns same bext data as manager.get_raw_metadata_info."""
        from audiometa._audio_file import _AudioFile
        from audiometa.manager._rating_supporting.riff._RiffManager import _RiffManager as RiffManager

        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_bext_description(test_file, "Test Description")
            RIFFMetadataSetter.set_bext_originator(test_file, "Test Originator")
            RIFFMetadataSetter.set_bext_time_reference(test_file, 44100)

            # Get via get_full_metadata
            result = get_full_metadata(test_file)
            bext_from_full = result.get("raw_metadata", {}).get("riff", {}).get("chunk_structure", {}).get("bext")

            # Get via manager directly
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()
            bext_from_manager = raw_info.get("chunk_structure", {}).get("bext")

            # Should be identical
            assert bext_from_full == bext_from_manager

    def test_bext_chunk_extraction_via_get_full_metadata_without_info_metadata(self):
        """Test that bext chunk is extracted via get_full_metadata even when no user-defined INFO metadata is present.

        This tests the code path at lines 899-901 in _RiffManager.py that ensures bext chunk
        extraction happens even when raw_clean_metadata is empty (no INFO metadata).
        """
        with temp_file_with_metadata({}, "wav") as test_file:
            # Add bext metadata but no user-defined INFO metadata
            RIFFMetadataSetter.set_bext_description(test_file, "Test Description")
            RIFFMetadataSetter.set_bext_originator(test_file, "Test Originator")

            result = get_full_metadata(test_file)

            riff_raw = result.get("raw_metadata", {}).get("riff", {})
            # Should still have bext chunk in chunk_structure regardless of INFO metadata
            assert "chunk_structure" in riff_raw
            assert "bext" in riff_raw["chunk_structure"]

            bext_data = riff_raw["chunk_structure"]["bext"]
            assert bext_data["Description"] == "Test Description"
            assert bext_data["Originator"] == "Test Originator"
