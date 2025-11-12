import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestPublisherReading:
    def test_id3v1(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v1") as test_file:
            publisher = get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER)
            assert publisher is None

    def test_id3v2(self):
        with temp_file_with_metadata({"title": "Test Song", "publisher": "Test Publisher"}, "mp3") as test_file:
            publisher = get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER)
            assert publisher == "Test Publisher"

    def test_vorbis(self):
        with temp_file_with_metadata({"title": "Test Song", "publisher": "Test Publisher"}, "flac") as test_file:
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "PUBLISHER=Test Publisher" in raw_metadata

            publisher = get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER)
            assert publisher == "Test Publisher"

    def test_riff(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            publisher = get_unified_metadata_field(test_file, UnifiedMetadataKey.PUBLISHER)
            assert publisher is None
