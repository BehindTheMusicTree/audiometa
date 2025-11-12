import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestCommentReading:
    def test_id3v1(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_max_metadata(test_file)
            comment = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT)
            assert comment == "a" * 28

    def test_id3v2(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_max_metadata(test_file)
            comment = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT)
            assert comment == "a" * 4000

    def test_vorbis(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_max_metadata(test_file)
            comment = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT)
            assert comment == "a" * 1000

    def test_riff(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_metadata(test_file, {"comment": "Test Comment RIFF"})
            comment = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMMENT)
            assert comment == "Test Comment RIFF"
