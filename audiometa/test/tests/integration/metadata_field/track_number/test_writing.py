import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestTrackNumberWriting:
    @pytest.mark.parametrize(
        ("input_value", "expected"),
        [
            (5, "5"),
            ("5", "5"),
            ("5/12", "5"),
            ("99/99", "99"),
        ],
    )
    def test_id3v1_track_number_writing(self, input_value, expected):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.TRACK_NUMBER: input_value}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V1)
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == expected

    @pytest.mark.parametrize(
        ("input_value", "expected"),
        [
            (5, "5"),
            ("5", "5"),
            ("5/12", "5/12"),
            ("99/99", "99/99"),
        ],
    )
    def test_id3v2_track_number_writing(self, input_value, expected):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_metadata = {UnifiedMetadataKey.TRACK_NUMBER: input_value}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2)
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == expected

    @pytest.mark.parametrize(
        ("input_value", "expected"),
        [
            (5, "5"),
            ("5", "5"),
            ("5/12", "5/12"),
            ("99/99", "99/99"),
        ],
    )
    def test_riff_track_number_writing(self, input_value, expected):
        with temp_file_with_metadata({}, "wav") as test_file:
            test_metadata = {UnifiedMetadataKey.TRACK_NUMBER: input_value}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.RIFF)
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == expected

    @pytest.mark.parametrize(
        ("input_value", "expected"),
        [
            (5, "5"),
            ("5", "5"),
            ("5/12", "5/12"),
            ("99/99", "99/99"),
        ],
    )
    def test_vorbis_track_number_writing(self, input_value, expected):
        with temp_file_with_metadata({}, "flac") as test_file:
            test_metadata = {UnifiedMetadataKey.TRACK_NUMBER: input_value}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.VORBIS)
            track_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.TRACK_NUMBER)
            assert track_number == expected
