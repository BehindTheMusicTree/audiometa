import pytest

from audiometa import update_metadata
from audiometa.exceptions import InvalidMetadataFieldFormatError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestReleaseDateErrorHandling:
    def test_invalid_format_wrong_separator_mp3(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            invalid_dates = [
                "2024/01/01",
                "2024.01.01",
                "2024 01 01",
            ]
            for invalid_date in invalid_dates:
                with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
                    update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: invalid_date})
                error = exc_info.value
                assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
                assert error.value == invalid_date

    def test_invalid_format_single_digit_mp3(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            invalid_dates = [
                "2024-1-1",
                "2024-1-01",
                "2024-01-1",
            ]
            for invalid_date in invalid_dates:
                with pytest.raises(InvalidMetadataFieldFormatError):
                    update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: invalid_date})

    def test_invalid_format_short_year_mp3(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            invalid_dates = ["24", "024", "999"]
            for invalid_date in invalid_dates:
                with pytest.raises(InvalidMetadataFieldFormatError):
                    update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: invalid_date})

    def test_invalid_format_non_numeric_mp3(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            invalid_dates = [
                "not-a-date",
                "2024-abc-01",
                "abcd-01-01",
            ]
            for invalid_date in invalid_dates:
                with pytest.raises(InvalidMetadataFieldFormatError):
                    update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: invalid_date})

    def test_invalid_format_wrong_separator_flac(self):
        with temp_file_with_metadata({}, "flac") as test_file, pytest.raises(InvalidMetadataFieldFormatError):
            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: "2024/01/01"})

    def test_invalid_format_wrong_separator_wav(self):
        with temp_file_with_metadata({}, "wav") as test_file, pytest.raises(InvalidMetadataFieldFormatError):
            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: "2024/01/01"})

    def test_valid_format_yyyy_passes(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: "2024"})

    def test_valid_format_yyyy_mm_dd_passes(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: "2024-01-01"})

    def test_none_value_allowed(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.RELEASE_DATE: None})

    def test_invalid_format_with_multiple_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file, pytest.raises(InvalidMetadataFieldFormatError):
            update_metadata(
                test_file,
                {
                    UnifiedMetadataKey.TITLE: "Valid Title",
                    UnifiedMetadataKey.RELEASE_DATE: "2024/01/01",
                },
            )
