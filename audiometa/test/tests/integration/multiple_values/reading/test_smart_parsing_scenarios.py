import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v1.id3v1_metadata_getter import ID3v1MetadataGetter
from audiometa.test.helpers.id3v1.id3v1_metadata_setter import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestSmartParsingScenarios:
    """Test the smart parsing scenarios described in the README:

    - Modern formats (ID3v2, Vorbis) + Multiple entries: No separator parsing
    - Modern formats (ID3v2, Vorbis) + Single entry: Applies separator parsing
    - Legacy formats (RIFF, ID3v1): Always applies separator parsing
    """

    def test_scenario_1_multiple_entries_no_parsing_id3v2_3(self):
        """Scenario 1: ID3v2.3 uses single frame with separators - gets parsed on read"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.3") as test_file:
            ID3v2MetadataSetter.set_artists(
                test_file,
                ["Artist One", "Artist; with; semicolons", "Artist Three"],
                version="2.3",
                in_separate_frames=True,
            )
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert raw_metadata["TPE1"] == ["Artist One", "Artist; with; semicolons", "Artist Three"]

            # Read metadata
            artists = get_unified_metadata_field(
                test_file,
                UnifiedMetadataKey.ARTISTS,
                metadata_format=MetadataFormat.ID3V2,
                id3v2_version=(2, 3, 0),
            )
            assert artists == ["Artist One", "Artist; with; semicolons", "Artist Three"]

    def test_scenario_1_multiple_entries_no_parsing_id3v2_4(self):
        """Scenario 1: ID3v2.4 uses single frame with separators - gets parsed on read"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set multiple separate artist entries (ID3v2.4 will concatenate them)
            ID3v2MetadataSetter.set_artists(
                test_file,
                ["Artist One", "Artist; with; semicolons", "Artist Three"],
                version="2.4",
                in_separate_frames=True,
            )
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.4")
            assert raw_metadata["TPE1"] == ["Artist One", "Artist; with; semicolons", "Artist Three"]

            # Read metadata
            artists = get_unified_metadata_field(
                test_file,
                UnifiedMetadataKey.ARTISTS,
                metadata_format=MetadataFormat.ID3V2,
                id3v2_version=(2, 4, 0),
            )
            assert artists == ["Artist One", "Artist; with; semicolons", "Artist Three"]

    def test_scenario_1_multiple_entries_no_parsing_vorbis(self):
        """Scenario 1: Modern file with separate entries - separators preserved (Vorbis)"""
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            # Set multiple separate artist entries (modern format)
            VorbisMetadataSetter.set_artists(test_file, ["Artist One", "Artist; with; semicolons", "Artist Three"])
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "ARTIST=Artist One" in raw_metadata
            assert "ARTIST=Artist; with; semicolons" in raw_metadata
            assert "ARTIST=Artist Three" in raw_metadata

            # Read metadata
            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS
            )
            assert artists == ["Artist One", "Artist; with; semicolons", "Artist Three"]

    def test_scenario_1_multiple_entries_no_parsing_riff(self):
        """Scenario 1: Modern file with separate entries - separators preserved (RIFF)"""
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            # Set multiple separate artist entries (modern format)
            RIFFMetadataSetter.set_artists(
                test_file, ["Artist One", "Artist; with; semicolons", "Artist Three"], in_separate_frames=True
            )
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "TAG:artist=Artist One" in raw_metadata
            assert "TAG:artist=Artist; with; semicolons" in raw_metadata
            assert "TAG:artist=Artist Three" in raw_metadata

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.RIFF
            )
            assert artists == ["Artist One", "Artist; with; semicolons", "Artist Three"]

    def test_scenario_2_single_entry_parsed_id3v2_3(self):
        """Scenario 2: Legacy data in modern format - single entry gets parsed (ID3v2.3)"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.3") as test_file:
            # Set single artist entry with semicolons (legacy data in modern format)
            ID3v2MetadataSetter.set_artists(
                test_file, ["Artist One;Artist Two;Artist Three"], version="2.3", in_separate_frames=False
            )

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert raw_metadata["TPE1"] == ["Artist One;Artist Two;Artist Three"]

            # Read metadata
            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )
            assert artists == ["Artist One", "Artist Two", "Artist Three"]

    def test_scenario_2_single_entry_parsed_id3v2_4(self):
        """Scenario 2: Legacy data in modern format - single entry gets parsed (ID3v2.4)"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set single artist entry with semicolons (legacy data in modern format)
            ID3v2MetadataSetter.set_artists(
                test_file, ["Artist One;Artist Two;Artist Three"], version="2.4", in_separate_frames=False
            )

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.4")
            assert raw_metadata["TPE1"] == ["Artist One;Artist Two;Artist Three"]

            # Read metadata
            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )
            assert artists == ["Artist One", "Artist Two", "Artist Three"]

    def test_scenario_2_single_entry_parsed_vorbis(self):
        """Scenario 2: Legacy data in modern format - single entry gets parsed (Vorbis)"""
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            # Set single artist entry with semicolons (legacy data in modern format)
            VorbisMetadataSetter.set_artists(test_file, ["Artist One;Artist Two;Artist Three"])
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "ARTIST=Artist One;Artist Two;Artist Three" in raw_metadata

            # Read metadata
            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS
            )
            assert artists == ["Artist One", "Artist Two", "Artist Three"]

    def test_scenario_2_single_entry_parsed_riff(self):
        """Scenario 3: Legacy format (RIFF) - always applies separator parsing"""
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            # Set single artist entry with semicolons in RIFF format
            RIFFMetadataSetter.set_artists(test_file, ["Artist One;Artist Two"], in_separate_frames=False)
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "TAG:artist=Artist One;Artist Two" in raw_metadata

            # Read metadata
            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.RIFF
            )
            assert artists == ["Artist One", "Artist Two"]

    def test_scenario_3_legacy_format_always_parses_id3v1(self):
        """Scenario 3: Legacy format (ID3v1) - always applies separator parsing"""
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            # Set single artist entry with semicolons in ID3v1 format
            ID3v1MetadataSetter.set_artist(test_file, "Artist One;Artist Two")
            raw_metadata = ID3v1MetadataGetter.get_raw_metadata(test_file)
            assert "Artist One;Artist Two" in raw_metadata.get("artist", "")

            # Read metadata
            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V1
            )
            assert artists == ["Artist One", "Artist Two"]

    def test_mixed_scenario_modern_format_with_both_patterns(self):
        """Test mixed scenario: ID3v2 concatenates multiple entries, single entries get parsed."""
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            # Set artists as multiple separate entries (ID3v2 will concatenate them)
            ID3v2MetadataSetter.set_artists(
                test_file,
                ["Artist One", "Artist; with; semicolons", "Artist Three"],
                version="2.3",
                in_separate_frames=True,
            )
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert raw_metadata["TPE1"] == ["Artist One", "Artist; with; semicolons", "Artist Three"]

            # Read metadata
            artists = get_unified_metadata_field(
                test_file,
                UnifiedMetadataKey.ARTISTS,
                metadata_format=MetadataFormat.ID3V2,
                id3v2_version=(2, 3, 0),
            )
            assert artists == ["Artist One", "Artist; with; semicolons", "Artist Three"]
