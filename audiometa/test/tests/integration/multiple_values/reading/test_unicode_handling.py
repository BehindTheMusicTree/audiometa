import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestUnicodeHandling:
    def test_unicode_characters(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist Café", "Artist 音乐", "Artist 🎵"])

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.VORBIS
            )

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist Café" in artists
            assert "Artist 音乐" in artists
            assert "Artist 🎵" in artists
