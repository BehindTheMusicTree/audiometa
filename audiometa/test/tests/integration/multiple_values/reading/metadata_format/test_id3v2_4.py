import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v2 import ID3v2HeaderVerifier, ID3v2MetadataGetter, ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestId3v24Mixed:
    def test_null_separated_artists(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_artists(test_file, ["Artist One", "Artist Two", "Artist Three"], version="2.4")

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.4")
            # raw_output replaces NUL bytes with slashes for display purposes
            assert raw_metadata["TPE1"] == ["Artist One\x00Artist Two\x00Artist Three"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert artists == ["Artist One", "Artist Two", "Artist Three"]

    def test_null_separated_artists_iso_8859_1(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Use a single NUL in the Python string; encoding=0 will encode it as a single 0x00
            ID3v2MetadataSetter.write_tpe1_with_encoding(
                test_file, "Artist One\x00Artist Two\x00Artist Three", encoding=0
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["TPE1"] == ["Artist One\x00Artist Two\x00Artist Three"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert artists == ["Artist One", "Artist Two", "Artist Three"]

    def test_null_separated_artists_utf16_with_bom(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Using a Python string with '\x00' — when encoded as UTF-16 it will become two zero bytes
            ID3v2MetadataSetter.write_tpe1_with_encoding(
                test_file, "Artist One\x00Artist Two\x00Artist Three", encoding=1
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["TPE1"] == ["Artist One\x00Artist Two\x00Artist Three"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert artists == ["Artist One", "Artist Two", "Artist Three"]

    def test_null_separated_artists_utf16be(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # ID3v2.4 with encoding=2 (UTF-16BE without BOM) — separator becomes two NUL bytes after encoding.
            ID3v2MetadataSetter.write_tpe1_with_encoding(
                test_file, "Artist One\x00Artist Two\x00Artist Three", encoding=2
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["TPE1"] == ["Artist One\x00Artist Two\x00Artist Three"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert artists == ["Artist One", "Artist Two", "Artist Three"]

    def test_null_separated_artists_utf8(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # ID3v2.4 with encoding=3 (UTF-8) — separator is a single NUL byte.
            ID3v2MetadataSetter.write_tpe1_with_encoding(
                test_file, "Artist One\x00Artist Two\x00Artist Three", encoding=3
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["TPE1"] == ["Artist One\x00Artist Two\x00Artist Three"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert artists == ["Artist One", "Artist Two", "Artist Three"]

    def test_semicolon_separated_artists(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_artists(test_file, "Artist One;Artist Two;Artist Three", version="2.4")

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["TPE1"] == ["Artist One;Artist Two;Artist Three"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert artists == ["Artist One", "Artist Two", "Artist Three"]

    def test_multiple_artists_in_multiple_entries_semicolon_separator(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_artists(
                test_file, ["Artist One;Artist Two", "Artist Three"], in_separate_frames=True, version="2.4"
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["TPE1"] == ["Artist One;Artist Two", "Artist Three"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(artists, list)
            assert len(artists) == 2
            assert artists == ["Artist One;Artist Two", "Artist Three"]

    def test_null_separated_artists_in_multiple_entries(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_artists(
                test_file, ["Artist One\0Artist Two", "Artist Three"], in_separate_frames=True, version="2.4"
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["TPE1"] == ["Artist One\0Artist Two", "Artist Three"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert artists == ["Artist One", "Artist Two", "Artist Three"]

    def test_null_separated_artists_in_multiple_entries_and_semicolon_separated(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_artists(
                test_file, ["Artist 1\0Artist 2", "Artist 3;Artist 4"], in_separate_frames=True, version="2.4"
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["TPE1"] == ["Artist 1\0Artist 2", "Artist 3;Artist 4"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert artists == ["Artist 1", "Artist 2", "Artist 3;Artist 4"]

    def test_mixed_separators_semicolon_and_null(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_artists(test_file, ["Artist 1\0Artist 2;Artist 3"], version="2.4")

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["TPE1"] == ["Artist 1\0Artist 2;Artist 3"]

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2
            )
            assert isinstance(artists, list)
            assert len(artists) == 2
            assert artists == ["Artist 1", "Artist 2;Artist 3"]

    def test_multiple_title_entries_then_first_one(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_titles(
                test_file, ["Title One", "Title Two", "Title Three"], in_separate_frames=True, version="2.4"
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["TIT2"] == ["Title One", "Title Two", "Title Three"]

            title = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.ID3V2
            )

            assert isinstance(title, str)
            assert title == "Title One"
