import pytest

from audiometa import get_unified_metadata_field
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestTrackNumberReadingEdgeCases:

    def test_trailing_slash(self):
        with TempFileWithMetadata({"track_number": "5/"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == 5

    def test_leading_slash_no_track(self):
        with TempFileWithMetadata({"track_number": "/12"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number is None

    def test_non_numeric_values(self):
        with TempFileWithMetadata({"track_number": "abc/def"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number is None

    def test_empty_string(self):
        with TempFileWithMetadata({"track_number": ""}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number is None

    def test_multiple_slashes(self):
        with TempFileWithMetadata({"track_number": "5/12/15"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number is None

    def test_different_separator(self):
        with TempFileWithMetadata({"track_number": "5-12"}, "mp3") as test_file:
            track_number = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == 5