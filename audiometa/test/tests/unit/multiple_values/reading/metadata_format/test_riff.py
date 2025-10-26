
from audiometa import get_unified_metadata_field
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter


class TestRiff:
    
    def test_semicolon_separated_artists(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_artists(test_file.path, ["Artist One;Artist Two;Artist Three"], in_separate_frames=False)
                        
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file.path)
            assert "TAG:artist=Artist One;Artist Two;Artist Three" in raw_metadata
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.RIFF)
            
            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist One" in artists
            assert "Artist Two" in artists
            assert "Artist Three" in artists

    def test_multiple_artists_in_multiple_entries(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_artists(test_file.path, ["One", "Two", "Three"], in_separate_frames=True)
            
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file.path)
            # ffprobe only shows the last field when multiple fields with the same tag exist
            assert "TAG:artist=Three" in raw_metadata
                      
            # Get RIFF metadata specifically to read the artists
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.RIFF)

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "One" in artists
            assert "Two" in artists
            assert "Three" in artists
            
    def test_mixed_separators_and_multiple_entries(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_artists(test_file.path, ["Artist 1;Artist 2", "Artist 3", "Artist 4"], in_separate_frames=True)

            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file.path)
            # ffprobe only shows the last field when multiple fields with the same tag exist
            assert "TAG:artist=Artist 4" in raw_metadata
            
            # Get RIFF metadata specifically to read the artists
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.RIFF)
            assert isinstance(artists, list)
            
            # We created 3 separate RIFF frames, so we should get 3 entries 
            # (separator parsing happens at a higher level, not in RIFF format itself)
            assert len(artists) == 3
            assert "Artist 1;Artist 2" in artists
            assert "Artist 3" in artists
            assert "Artist 4" in artists
            
    def test_multiple_title_entries_then_first_one(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_multiple_titles(test_file.path, ["Title One", "Title Two", "Title Three"], in_separate_frames=True)

            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file.path)
            # ffprobe only shows the last field when multiple fields with the same tag exist
            assert "TAG:title=Title Three" in raw_metadata
            
            title = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.RIFF)
            assert isinstance(title, str)
            assert title == "Title One"