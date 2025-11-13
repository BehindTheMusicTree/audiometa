import pytest

from audiometa import get_unified_metadata_field
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestLyricsReading:
    def test_id3v1(self):
        with (
            temp_file_with_metadata({"title": "Test Song"}, "id3v1") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS metadata not supported by ID3v1 format",
            ),
        ):
            get_unified_metadata_field(
                test_file, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS, metadata_format=MetadataFormat.ID3V1
            )

    def test_id3v2_3(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.3") as test_file:
            ID3v2MetadataSetter.set_lyrics(test_file, "a" * 4000, version="2.3")
            lyrics = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS, metadata_format=MetadataFormat.ID3V2
            )
            assert lyrics == "a" * 4000

    def test_id3v2_4(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_lyrics(test_file, "a" * 4000, version="2.4")
            lyrics = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS, metadata_format=MetadataFormat.ID3V2
            )
            assert lyrics == "a" * 4000

    def test_vorbis(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_lyrics(test_file, "a" * 4000)
            lyrics = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS, metadata_format=MetadataFormat.VORBIS
            )
            assert lyrics == "a" * 4000

    def test_riff(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_lyrics(test_file, "a" * 4000)
            lyrics = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS, metadata_format=MetadataFormat.RIFF
            )
            assert lyrics == "a" * 4000
