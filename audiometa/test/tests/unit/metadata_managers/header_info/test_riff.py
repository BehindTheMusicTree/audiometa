"""Unit tests for RIFF metadata manager header information methods."""

from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile
from audiometa.manager._rating_supporting.riff._RiffManager import _RiffManager as RiffManager
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.unit
class TestRiffHeaderMethods:
    """Test cases for RIFF metadata manager header information methods."""

    def test_riff_manager_header_info(self, sample_wav_file: Path):
        """Test RiffManager header info method."""
        audio_file = _AudioFile(sample_wav_file)
        manager = RiffManager(audio_file)

        header_info = manager.get_header_info()

        # Should have RIFF specific structure
        assert "present" in header_info
        assert "chunk_info" in header_info

        # Should be valid structure
        assert isinstance(header_info["present"], bool)
        assert isinstance(header_info["chunk_info"], dict)

        # Chunk info should have expected keys
        chunk_info = header_info["chunk_info"]
        if header_info["present"]:
            assert "riff_chunk_size" in chunk_info
            assert "info_chunk_size" in chunk_info
            assert "audio_format" in chunk_info
            assert "subchunk_size" in chunk_info

    def test_riff_manager_raw_metadata_info(self, sample_wav_file: Path):
        """Test RiffManager raw metadata info method."""
        audio_file = _AudioFile(sample_wav_file)
        manager = RiffManager(audio_file)

        raw_info = manager.get_raw_metadata_info()

        # Should have RIFF specific structure
        assert "raw_data" in raw_info
        assert "parsed_fields" in raw_info
        assert "frames" in raw_info
        assert "comments" in raw_info
        assert "chunk_structure" in raw_info

        # Should be valid structure
        assert raw_info["raw_data"] is None or isinstance(raw_info["raw_data"], bytes)
        assert isinstance(raw_info["parsed_fields"], dict)
        assert isinstance(raw_info["frames"], dict)
        assert isinstance(raw_info["comments"], dict)
        assert isinstance(raw_info["chunk_structure"], dict)

    def test_riff_manager_bext_chunk_extraction_with_description(self):
        """Test RIFF manager bext chunk extraction with Description field."""
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_bext_description(test_file, "Test Description")

            # Verify using external tool
            external_bext = RIFFMetadataGetter.get_bext_metadata(test_file)
            assert external_bext.get("Description") == "Test Description"

            # Verify using our extraction
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()

            assert "chunk_structure" in raw_info
            assert "bext" in raw_info["chunk_structure"]
            bext_data = raw_info["chunk_structure"]["bext"]
            assert bext_data["Description"] == "Test Description"
            # Verify our extraction matches external tool
            assert bext_data["Description"] == external_bext.get("Description")

    def test_riff_manager_bext_chunk_extraction_with_originator(self):
        """Test RIFF manager bext chunk extraction with Originator field."""
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_bext_originator(test_file, "Test Originator")

            # Verify using external tool
            external_bext = RIFFMetadataGetter.get_bext_metadata(test_file)
            assert external_bext.get("Originator") == "Test Originator"

            # Verify using our extraction
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()

            assert "chunk_structure" in raw_info
            assert "bext" in raw_info["chunk_structure"]
            bext_data = raw_info["chunk_structure"]["bext"]
            assert bext_data["Originator"] == "Test Originator"
            # Verify our extraction matches external tool
            assert bext_data["Originator"] == external_bext.get("Originator")

    def test_riff_manager_bext_chunk_extraction_with_originator_reference(self):
        """Test RIFF manager bext chunk extraction with OriginatorReference field."""
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_bext_originator_reference(test_file, "REF-12345")

            # Verify using external tool
            external_bext = RIFFMetadataGetter.get_bext_metadata(test_file)
            assert external_bext.get("OriginatorReference") == "REF-12345"

            # Verify using our extraction
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()

            assert "chunk_structure" in raw_info
            assert "bext" in raw_info["chunk_structure"]
            bext_data = raw_info["chunk_structure"]["bext"]
            assert bext_data["OriginatorReference"] == "REF-12345"
            assert bext_data["OriginatorReference"] == external_bext.get("OriginatorReference")

    def test_riff_manager_bext_chunk_extraction_with_origination_date(self):
        """Test RIFF manager bext chunk extraction with OriginationDate field."""
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_bext_origination_date(test_file, "2024-01-15")

            # Verify using external tool
            external_bext = RIFFMetadataGetter.get_bext_metadata(test_file)
            assert external_bext.get("OriginationDate") == "2024-01-15"

            # Verify using our extraction
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()

            assert "chunk_structure" in raw_info
            assert "bext" in raw_info["chunk_structure"]
            bext_data = raw_info["chunk_structure"]["bext"]
            assert bext_data["OriginationDate"] == "2024-01-15"
            assert bext_data["OriginationDate"] == external_bext.get("OriginationDate")

    def test_riff_manager_bext_chunk_extraction_with_origination_time(self):
        """Test RIFF manager bext chunk extraction with OriginationTime field."""
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_bext_origination_time(test_file, "14:30:00")

            # Verify using external tool
            external_bext = RIFFMetadataGetter.get_bext_metadata(test_file)
            assert external_bext.get("OriginationTime") == "14:30:00"

            # Verify using our extraction
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()

            assert "chunk_structure" in raw_info
            assert "bext" in raw_info["chunk_structure"]
            bext_data = raw_info["chunk_structure"]["bext"]
            assert bext_data["OriginationTime"] == "14:30:00"
            assert bext_data["OriginationTime"] == external_bext.get("OriginationTime")

    def test_riff_manager_bext_chunk_extraction_with_time_reference(self):
        """Test RIFF manager bext chunk extraction with TimeReference field."""
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_bext_time_reference(test_file, 44100)

            # Verify using external tool
            external_bext = RIFFMetadataGetter.get_bext_metadata(test_file)
            assert external_bext.get("TimeReference") == 44100

            # Verify using our extraction
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()

            assert "chunk_structure" in raw_info
            assert "bext" in raw_info["chunk_structure"]
            bext_data = raw_info["chunk_structure"]["bext"]
            assert bext_data["TimeReference"] == 44100
            assert bext_data["TimeReference"] == external_bext.get("TimeReference")

    def test_riff_manager_bext_chunk_extraction_with_coding_history(self):
        """Test RIFF manager bext chunk extraction with CodingHistory field."""
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_bext_coding_history(test_file, "A=PCM,F=44100,W=16,M=mono,T=PCM")

            # Verify using external tool
            external_bext = RIFFMetadataGetter.get_bext_metadata(test_file)
            assert external_bext.get("CodingHistory") == "A=PCM,F=44100,W=16,M=mono,T=PCM"

            # Verify using our extraction
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()

            assert "chunk_structure" in raw_info
            assert "bext" in raw_info["chunk_structure"]
            bext_data = raw_info["chunk_structure"]["bext"]
            assert bext_data["CodingHistory"] == "A=PCM,F=44100,W=16,M=mono,T=PCM"
            assert bext_data["CodingHistory"] == external_bext.get("CodingHistory")

    def test_riff_manager_bext_chunk_extraction_with_multiple_fields(self):
        """Test RIFF manager bext chunk extraction with multiple fields."""
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

            # Verify using external tool
            external_bext = RIFFMetadataGetter.get_bext_metadata(test_file)

            # Verify using our extraction
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()

            assert "chunk_structure" in raw_info
            assert "bext" in raw_info["chunk_structure"]
            bext_data = raw_info["chunk_structure"]["bext"]

            # Verify each field matches external tool
            assert bext_data["Description"] == "Test Description"
            assert bext_data["Description"] == external_bext.get("Description")
            assert bext_data["Originator"] == "Test Originator"
            assert bext_data["Originator"] == external_bext.get("Originator")
            assert bext_data["OriginatorReference"] == "REF-12345"
            assert bext_data["OriginatorReference"] == external_bext.get("OriginatorReference")
            assert bext_data["OriginationDate"] == "2024-01-15"
            assert bext_data["OriginationDate"] == external_bext.get("OriginationDate")
            assert bext_data["OriginationTime"] == "14:30:00"
            assert bext_data["OriginationTime"] == external_bext.get("OriginationTime")
            assert bext_data["TimeReference"] == 44100
            assert bext_data["TimeReference"] == external_bext.get("TimeReference")
            assert bext_data["CodingHistory"] == "A=PCM,F=44100,W=16,M=mono,T=PCM"
            assert bext_data["CodingHistory"] == external_bext.get("CodingHistory")

    def test_riff_manager_bext_chunk_extraction_without_bext_chunk(self, sample_wav_file: Path):
        """Test that regular WAV files without bext chunk return empty chunk_structure."""
        audio_file = _AudioFile(sample_wav_file)
        manager = RiffManager(audio_file)
        raw_info = manager.get_raw_metadata_info()

        assert "chunk_structure" in raw_info
        # Regular WAV files without bext chunk should not have bext in chunk_structure
        assert "bext" not in raw_info["chunk_structure"]

    def test_riff_manager_bext_chunk_extraction_without_info_metadata(self):
        """Test that bext chunk is extracted even when no user-defined RIFF INFO metadata is present.

        This tests the code path at lines 899-901 in _RiffManager.py that ensures bext chunk
        extraction happens even when raw_clean_metadata is empty (no INFO metadata).
        """
        with temp_file_with_metadata({}, "wav") as test_file:
            # Add bext metadata but no user-defined INFO metadata
            RIFFMetadataSetter.set_bext_description(test_file, "Test Description")
            RIFFMetadataSetter.set_bext_originator(test_file, "Test Originator")

            # Verify using external tool
            external_bext = RIFFMetadataGetter.get_bext_metadata(test_file)
            assert external_bext.get("Description") == "Test Description"
            assert external_bext.get("Originator") == "Test Originator"

            # Verify using our extraction
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()

            # Should still have bext chunk in chunk_structure regardless of INFO metadata
            assert "chunk_structure" in raw_info
            assert "bext" in raw_info["chunk_structure"]
            bext_data = raw_info["chunk_structure"]["bext"]
            assert bext_data["Description"] == "Test Description"
            assert bext_data["Originator"] == "Test Originator"
            # Verify our extraction matches external tool
            assert bext_data["Description"] == external_bext.get("Description")
            assert bext_data["Originator"] == external_bext.get("Originator")

    def test_riff_manager_bext_chunk_extraction_with_loudness_metadata(self):
        """Test RIFF manager bext chunk extraction with BWF v2 loudness metadata fields."""
        with temp_file_with_metadata({}, "wav") as test_file:
            # Set bext metadata including loudness fields (requires BWF v2)
            RIFFMetadataSetter.set_bext_metadata(
                test_file,
                {
                    "Description": "Test Description",
                    "LoudnessValue": -23.0,
                    "LoudnessRange": 7.0,
                    "MaxTruePeakLevel": -1.5,
                    "MaxMomentaryLoudness": -22.0,
                    "MaxShortTermLoudness": -22.5,
                },
            )

            # Verify using external tool
            external_bext = RIFFMetadataGetter.get_bext_metadata(test_file)
            assert external_bext.get("Description") == "Test Description"
            assert external_bext.get("LoudnessValue") == pytest.approx(-23.0, abs=0.1)
            assert external_bext.get("LoudnessRange") == pytest.approx(7.0, abs=0.1)
            assert external_bext.get("MaxTruePeakLevel") == pytest.approx(-1.5, abs=0.1)
            assert external_bext.get("MaxMomentaryLoudness") == pytest.approx(-22.0, abs=0.1)
            assert external_bext.get("MaxShortTermLoudness") == pytest.approx(-22.5, abs=0.1)

            # Verify using our extraction
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)
            raw_info = manager.get_raw_metadata_info()

            assert "chunk_structure" in raw_info
            assert "bext" in raw_info["chunk_structure"]
            bext_data = raw_info["chunk_structure"]["bext"]

            # Verify version is 2 (BWF v2)
            assert bext_data.get("Version") == 2

            # Verify loudness fields match external tool
            assert bext_data["Description"] == "Test Description"
            assert bext_data.get("LoudnessValue") == pytest.approx(-23.0, abs=0.1)
            assert bext_data.get("LoudnessRange") == pytest.approx(7.0, abs=0.1)
            assert bext_data.get("MaxTruePeakLevel") == pytest.approx(-1.5, abs=0.1)
            assert bext_data.get("MaxMomentaryLoudness") == pytest.approx(-22.0, abs=0.1)
            assert bext_data.get("MaxShortTermLoudness") == pytest.approx(-22.5, abs=0.1)

            # Verify our extraction matches external tool
            assert bext_data.get("LoudnessValue") == pytest.approx(external_bext.get("LoudnessValue", 0), abs=0.1)
            assert bext_data.get("LoudnessRange") == pytest.approx(external_bext.get("LoudnessRange", 0), abs=0.1)
            assert bext_data.get("MaxTruePeakLevel") == pytest.approx(external_bext.get("MaxTruePeakLevel", 0), abs=0.1)
            assert bext_data.get("MaxMomentaryLoudness") == pytest.approx(
                external_bext.get("MaxMomentaryLoudness", 0), abs=0.1
            )
            assert bext_data.get("MaxShortTermLoudness") == pytest.approx(
                external_bext.get("MaxShortTermLoudness", 0), abs=0.1
            )
