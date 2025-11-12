import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestTrackNumberReadingEdgeCases:
    def test_trailing_slash(self):
        with temp_file_with_metadata({"track_number": "5/"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == "5/"

    def test_leading_slash_no_track(self):
        with temp_file_with_metadata({"track_number": "/12"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number is None

    def test_non_numeric_values(self):
        with temp_file_with_metadata({"track_number": "abc/def"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number is None

    def test_empty_string(self):
        with temp_file_with_metadata({"track_number": ""}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number is None

    def test_multiple_slashes(self):
        with temp_file_with_metadata({"track_number": "5/12/15"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number is None

    def test_different_separator(self):
        with temp_file_with_metadata({"track_number": "5-12"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == "5-12"

    def test_leading_zeros_preserved(self):
        with temp_file_with_metadata({"track_number": "01"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == "01"
