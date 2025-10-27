import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestAlbumArtistsReading:
    def test_id3v1(self):
        with TempFileWithMetadata({"title": "Test Song"}, "id3v1") as test_file:
            album_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS)
            assert album_artists is None

    def test_id3v2(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_max_metadata(test_file.path)
            album_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS)
            assert album_artists == ["a" * 1000]

    def test_vorbis(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_max_metadata(test_file.path)
            album_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS)
            assert album_artists == ["a" * 1000]

    def test_riff(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_multiple_album_artists(test_file.path, ["Test Album Artist"])
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file.path)
            assert "TAG:IAAR=Test Album Artist" in raw_metadata
            
            album_artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ALBUM_ARTISTS)
            assert album_artists == ["Test Album Artist"]
