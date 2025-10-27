
import pytest

from audiometa import get_unified_metadata_field
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter


@pytest.mark.integration
class TestLyricsReading:
    def test_id3v1(self):
        with TempFileWithMetadata({"title": "Test Song"}, "id3v1") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError, match="UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS metadata not supported by this format"):
                get_unified_metadata_field(test_file.path, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS, metadata_format=MetadataFormat.ID3V1)

    def test_id3v2_3(self):
        with TempFileWithMetadata({"title": "Test Song"}, "id3v2.3") as test_file:
            ID3v2MetadataSetter.set_lyrics(test_file.path, "a" * 4000, version='2.3')
            lyrics = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS, metadata_format=MetadataFormat.ID3V2)
            assert lyrics == "a" * 4000
            
    def test_id3v2_4(self):
        with TempFileWithMetadata({"title": "Test Song"}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_lyrics(test_file.path, "a" * 4000, version='2.4')
            lyrics = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS, metadata_format=MetadataFormat.ID3V2)
            assert lyrics == "a" * 4000

    def test_vorbis(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_lyrics(test_file.path, "a" * 4000)
            lyrics = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS, metadata_format=MetadataFormat.VORBIS)
            assert lyrics == "a" * 4000

    def test_riff(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_lyrics(test_file.path, "a" * 4000)
            lyrics = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS, metadata_format=MetadataFormat.RIFF)
            assert lyrics == "a" * 4000
