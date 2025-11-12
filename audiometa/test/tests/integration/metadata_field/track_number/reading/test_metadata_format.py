import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v1.id3v1_metadata_getter import ID3v1MetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestTrackNumberReading:
    def test_id3v1_1(self):
        with temp_file_with_metadata({"title": "Test Song", "track": "99"}, "id3v1") as test_file:
            raw_metadata = ID3v1MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata.get("track") == 99

            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == "99"

    def test_id3v2(self):
        with temp_file_with_metadata({"title": "Test Song", "track_number": "99/99"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == "99/99"

    def test_vorbis(self):
        with temp_file_with_metadata({"title": "Test Song", "track_number": "99"}, "flac") as test_file:
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == "99"

    def test_riff(self):
        with temp_file_with_metadata({"title": "Test Song", "track_number": None}, "wav") as test_file:
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number is None
