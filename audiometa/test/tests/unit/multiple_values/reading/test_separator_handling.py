
from audiometa import get_unified_metadata_field
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.utils.MetadataFormat import MetadataFormat


class TestSeparatorHandling:

    # All tests follow the pattern: set a single value with all separators, check parsed list
    def test_separator_priority_double_slash(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            value = "Artist One//Artist Two;Artist Three,Artist Four/Artist Five\\Artist Six"
            ID3v2MetadataSetter.set_artists(test_file.path, [value])
            api_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2)
            assert api_artists == ["Artist One", "Artist Two;Artist Three,Artist Four/Artist Five\\Artist Six"]

    def test_separator_priority_double_backslash(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            value = "Artist One\\Artist Two;Artist Three,Artist Four/Artist Five"
            ID3v2MetadataSetter.set_artists(test_file.path, [value])
            api_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2)
            assert api_artists == ["Artist One", "Artist Two;Artist Three,Artist Four/Artist Five"]

    def test_separator_priority_semicolon(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            value = "Artist One;Artist Two,Artist Three/Artist Four"
            ID3v2MetadataSetter.set_artists(test_file.path, [value])
            api_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2)
            assert api_artists == ["Artist One", "Artist Two,Artist Three/Artist Four"]
    
    def test_separator_priority_backslash(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            value = "Artist One\\Artist Two,Artist Three/Artist Four"
            ID3v2MetadataSetter.set_artists(test_file.path, [value])
            api_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2)
            assert api_artists == ["Artist One", "Artist Two,Artist Three/Artist Four"]

    def test_separator_priority_slash(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            value = "Artist One/Artist Two,Artist Three"
            ID3v2MetadataSetter.set_artists(test_file.path, [value])
            api_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2)
            assert api_artists == ["Artist One", "Artist Two,Artist Three"]

    def test_separator_priority_comma(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            value = "Artist One,Artist Two"
            ID3v2MetadataSetter.set_artists(test_file.path, [value])
            api_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V2)
            assert api_artists == ["Artist One", "Artist Two"]