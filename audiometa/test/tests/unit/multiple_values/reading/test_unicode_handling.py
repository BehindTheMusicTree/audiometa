import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


class TestUnicodeHandling:
    def test_unicode_characters(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file.path, [
                "Artist Café",
                "Artist 音乐",
                "Artist 🎵"
            ])
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS)
            
            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist Café" in artists
            assert "Artist 音乐" in artists
            assert "Artist 🎵" in artists
