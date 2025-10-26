
from audiometa import get_unified_metadata_field
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v1.id3v1_metadata_setter import ID3v1MetadataSetter


class TestId3v1:
    def test_semicolon_separated_artists(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_artist(test_file.path, "Artist One;Artist Two")
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V1)
            
            assert isinstance(artists, list)
            assert len(artists) == 2
            assert "Artist One" in artists
            assert "Artist Two" in artists