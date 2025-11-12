import pytest

from audiometa import _validate_unified_metadata_types
from audiometa.exceptions import InvalidMetadataFieldFormatError, InvalidMetadataFieldTypeError
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.unit
class TestReleaseDateFormatValidation:
    def test_valid_yyyy_format(self):
        valid_years = ["2024", "1900", "0000", "9999", "1970"]
        for year in valid_years:
            _validate_unified_metadata_types({UnifiedMetadataKey.RELEASE_DATE: year})

    def test_valid_yyyy_mm_dd_format(self):
        valid_dates = [
            "2024-01-01",
            "2024-12-31",
            "1900-01-01",
            "0000-00-00",
            "9999-12-31",
            "1970-06-15",
        ]
        for date in valid_dates:
            _validate_unified_metadata_types({UnifiedMetadataKey.RELEASE_DATE: date})

    def test_invalid_format_wrong_separator(self):
        invalid_dates = [
            "2024/01/01",
            "2024.01.01",
            "2024_01_01",
            "2024 01 01",
        ]
        for date in invalid_dates:
            with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
                _validate_unified_metadata_types({UnifiedMetadataKey.RELEASE_DATE: date})
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
            assert error.value == date
            assert "YYYY" in error.expected_format

    def test_invalid_format_single_digit_month_day(self):
        invalid_dates = [
            "2024-1-1",
            "2024-1-01",
            "2024-01-1",
        ]
        for date in invalid_dates:
            with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
                _validate_unified_metadata_types({UnifiedMetadataKey.RELEASE_DATE: date})
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
            assert error.value == date

    def test_invalid_format_short_year(self):
        invalid_dates = [
            "24",
            "024",
            "999",
        ]
        for date in invalid_dates:
            with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
                _validate_unified_metadata_types({UnifiedMetadataKey.RELEASE_DATE: date})
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
            assert error.value == date

    def test_invalid_format_long_year(self):
        invalid_dates = [
            "20241",
            "20241-01-01",
        ]
        for date in invalid_dates:
            with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
                _validate_unified_metadata_types({UnifiedMetadataKey.RELEASE_DATE: date})
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
            assert error.value == date

    def test_invalid_format_non_numeric(self):
        invalid_dates = [
            "not-a-date",
            "2024-abc-01",
            "abcd-01-01",
            "2024-01-abc",
            "2024a",
        ]
        for date in invalid_dates:
            with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
                _validate_unified_metadata_types({UnifiedMetadataKey.RELEASE_DATE: date})
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
            assert error.value == date

    def test_invalid_format_incomplete_date(self):
        invalid_dates = [
            "2024-",
            "2024-01",
            "2024-01-",
            "-01-01",
        ]
        for date in invalid_dates:
            with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
                _validate_unified_metadata_types({UnifiedMetadataKey.RELEASE_DATE: date})
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
            assert error.value == date

    def test_none_value_allowed(self):
        _validate_unified_metadata_types({UnifiedMetadataKey.RELEASE_DATE: None})

    def test_empty_string_allowed(self):
        _validate_unified_metadata_types({UnifiedMetadataKey.RELEASE_DATE: ""})

    def test_format_validation_after_type_validation(self):
        invalid_type = {UnifiedMetadataKey.RELEASE_DATE: 2024}
        with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
            _validate_unified_metadata_types(invalid_type)
        assert not isinstance(exc_info.value, InvalidMetadataFieldFormatError)
