import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestVorbis:
    def test_null_value_separated_artists(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(
                test_file, ["Artist One", "Artist Two", "Artist Three"], in_single_entry=True
            )

            raw_metadata = VorbisMetadataGetter.get_raw_metadata_without_truncating_null_bytes_but_lower_case_keys(
                test_file
            )
            # The key is lower case because that is how mutagen stores it but it is upper case in the file
            assert "artist=Artist One\x00Artist Two\x00Artist Three" in raw_metadata

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS
            )
            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist One" in artists
            assert "Artist Two" in artists
            assert "Artist Three" in artists

    def test_null_separated_artists_with_additional_entries(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist A", "Artist B"], in_single_entry=True)
            VorbisMetadataSetter.set_artists(
                test_file, ["Artist C", "Artist D"], removing_existing=False, in_single_entry=True
            )

            raw_metadata = VorbisMetadataGetter.get_raw_metadata_without_truncating_null_bytes_but_lower_case_keys(
                test_file
            )
            # The key is lower case because that is how mutagen stores it but it is upper case in the file
            assert "artist=Artist A\x00Artist B" in raw_metadata
            assert "artist=Artist C\x00Artist D" in raw_metadata

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS
            )
            assert isinstance(artists, list)
            assert len(artists) == 4
            assert "Artist A" in artists
            assert "Artist B" in artists
            assert "Artist C" in artists
            assert "Artist D" in artists

    def test_null_separated_artists_in_multiple_entries_with_semicolon(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist One\x00Artist Two", "Artist Three;Artist Four"])

            raw_metadata = VorbisMetadataGetter.get_raw_metadata_without_truncating_null_bytes_but_lower_case_keys(
                test_file
            )
            assert "artist=Artist One\x00Artist Two" in raw_metadata
            assert "artist=Artist Three;Artist Four" in raw_metadata

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS
            )
            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist One" in artists
            assert "Artist Two" in artists
            assert "Artist Three;Artist Four" in artists

    def test_semicolon_separated_artists(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist One;Artist Two;Artist Three"])

            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "ARTIST=Artist One;Artist Two;Artist Three" in raw_metadata

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS
            )
            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist One" in artists
            assert "Artist Two" in artists
            assert "Artist Three" in artists

    def test_artists_in_multiple_entries(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["One", "Two", "Three"])

            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "ARTIST=One" in raw_metadata
            assert "ARTIST=Two" in raw_metadata
            assert "ARTIST=Three" in raw_metadata

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "One" in artists
            assert "Two" in artists
            assert "Three" in artists

    def test_artists_in_multiple_entries_with_different_key_casings(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist A", "Artist B"])
            VorbisMetadataSetter.set_artists(
                test_file, ["Artist C", "Artist D"], removing_existing=False, key_lower_case=True
            )

            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "artist=Artist A" in raw_metadata
            assert "artist=Artist B" in raw_metadata
            assert "artist=Artist C" in raw_metadata
            assert "artist=Artist D" in raw_metadata

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS
            )

            assert isinstance(artists, list)
            assert len(artists) == 4
            assert "Artist A" in artists
            assert "Artist B" in artists
            assert "Artist C" in artists
            assert "Artist D" in artists

    def test_mixed_single_and_multiple_entries(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist 1;Artist 2", "Artist 3", "Artist 4"])

            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)

            assert "ARTIST=Artist 1;Artist" in raw_metadata
            assert "ARTIST=Artist 3" in raw_metadata
            assert "ARTIST=Artist 4" in raw_metadata

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS
            )
            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist 1;Artist 2" in artists
            assert "Artist 3" in artists
            assert "Artist 4" in artists

    def test_multiple_title_entries_returns_first_value(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.add_title(test_file, "Title One")
            VorbisMetadataSetter.add_title(test_file, "Title Two")
            VorbisMetadataSetter.add_title(test_file, "Title Three")

            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "TITLE=Title One" in raw_metadata
            assert "TITLE=Title Two" in raw_metadata
            assert "TITLE=Title Three" in raw_metadata

            title = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.VORBIS
            )
            assert title == "Title One"
