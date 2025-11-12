import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestLanguageReading:
    def test_id3v1(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_max_metadata(test_file)
            language = get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE)
            assert language is None

    def test_id3v2(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_max_metadata(test_file)
            language = get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE)
            assert language == "a" * 1000

    def test_vorbis(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_max_metadata(test_file)
            language = get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE)
            assert language == "a" * 1000

    def test_riff(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_language(test_file, "en")
            assert "TAG:language=en" in RIFFMetadataGetter.get_raw_metadata(test_file)

            language = get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE)
            assert language == "en"
