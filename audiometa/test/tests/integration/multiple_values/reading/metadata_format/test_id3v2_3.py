import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v2 import ID3v2HeaderVerifier
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestId3v23:
    def test_semicolon_separated_artists(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_artists(
                test_file, ["Artist One;Artist Two;Artist Three"], in_separate_frames=False, version="2.3"
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 3, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert raw_metadata["TPE1"] == ["Artist One;Artist Two;Artist Three"]

            artists = get_unified_metadata_field(
                test_file,
                unified_metadata_key=UnifiedMetadataKey.ARTISTS,
                metadata_format=MetadataFormat.ID3V2,
                id3v2_version=(2, 3, 0),
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist One" in artists
            assert "Artist Two" in artists
            assert "Artist Three" in artists

    def test_multiple_entries(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_artists(test_file, ["One", "Two", "Three"], version="2.3", in_separate_frames=True)

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 3, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert raw_metadata["TPE1"] == ["One", "Two", "Three"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "One" in artists
            assert "Two" in artists
            assert "Three" in artists

    def test_mixed_separators_and_multiple_entries(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.3") as test_file:
            ID3v2MetadataSetter.set_artists(
                test_file, ["Artist 1;Artist 2", "Artist 3"], version="2.3", in_separate_frames=True
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 3, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert raw_metadata["TPE1"] == ["Artist 1;Artist 2", "Artist 3"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )
            assert isinstance(artists, list)
            assert len(artists) == 2
            assert "Artist 1;Artist 2" in artists
            assert "Artist 3" in artists

    def test_multiple_title_entries_then_first_one(self):
        with temp_file_with_metadata({"title": "Initial Title"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_titles(
                test_file, ["Title One", "Title Two", "Title Three"], version="2.3", in_separate_frames=True
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 3, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert raw_metadata["TIT2"] == ["Title One", "Title Two", "Title Three"]

            title = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(title, str)
            assert title == "Title One"
