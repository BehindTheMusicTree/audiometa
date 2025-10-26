

import pytest

from audiometa import get_unified_metadata_field
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.test.helpers.riff import RIFFMetadataSetter


@pytest.mark.integration
class TestArtistsReading:
    def test_id3v1(self):
        with TempFileWithMetadata({"title": "Test Song"}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_max_metadata(test_file.path)
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            assert artists == ["a" * 30]

    def test_id3v2(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_max_metadata(test_file.path)
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            assert artists == ["a" * 1000]

    def test_vorbis(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_max_metadata(test_file.path)
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            assert artists == ["a" * 1000]

    def test_riff(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_max_metadata(test_file.path)
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            assert artists == ["a" * 1000]
