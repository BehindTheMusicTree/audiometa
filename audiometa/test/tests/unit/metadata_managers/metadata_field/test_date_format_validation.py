import pytest

from audiometa import validate_metadata_for_update
from audiometa.exceptions import InvalidMetadataFieldFormatError, InvalidMetadataFieldTypeError
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestReleaseDateFormatValidation:
    @pytest.mark.parametrize(
        "year",
        ["2024", "1900", "0000", "9999", "1970"],
    )
    def test_valid_yyyy_format(self, year):
        validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: year})

    @pytest.mark.parametrize(
        "date",
        [
            "2024-01-01",
            "2024-12-31",
            "1900-01-01",
            "0000-00-00",
            "9999-12-31",
            "1970-06-15",
        ],
    )
    def test_valid_yyyy_mm_dd_format(self, date):
        validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: date})

    @pytest.mark.parametrize(
        "date",
        [
            "2024/01/01",
            "2024.01.01",
            "2024_01_01",
            "2024 01 01",
        ],
    )
    def test_invalid_format_wrong_separator(self, date):
        with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: date})
        error = exc_info.value
        assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
        assert error.value == date
        assert "YYYY" in error.expected_format

    @pytest.mark.parametrize(
        "date",
        [
            "2024-1-1",
            "2024-1-01",
            "2024-01-1",
        ],
    )
    def test_invalid_format_single_digit_month_day(self, date):
        with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: date})
        error = exc_info.value
        assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
        assert error.value == date

    @pytest.mark.parametrize(
        "date",
        [
            "24",
            "024",
            "999",
        ],
    )
    def test_invalid_format_short_year(self, date):
        with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: date})
        error = exc_info.value
        assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
        assert error.value == date

    @pytest.mark.parametrize(
        "date",
        [
            "20241",
            "20241-01-01",
        ],
    )
    def test_invalid_format_long_year(self, date):
        with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: date})
        error = exc_info.value
        assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
        assert error.value == date

    @pytest.mark.parametrize(
        "date",
        [
            "not-a-date",
            "2024-abc-01",
            "abcd-01-01",
            "2024-01-abc",
            "2024a",
        ],
    )
    def test_invalid_format_non_numeric(self, date):
        with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: date})
        error = exc_info.value
        assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
        assert error.value == date

    @pytest.mark.parametrize(
        "date",
        [
            "2024-",
            "2024-01",
            "2024-01-",
            "-01-01",
        ],
    )
    def test_invalid_format_incomplete_date(self, date):
        with pytest.raises(InvalidMetadataFieldFormatError) as exc_info:
            validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: date})
        error = exc_info.value
        assert error.field == UnifiedMetadataKey.RELEASE_DATE.value
        assert error.value == date

    def test_none_value_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: None})

    def test_empty_string_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: ""})

    def test_format_validation_after_type_validation(self):
        invalid_type = {UnifiedMetadataKey.RELEASE_DATE: 2024}
        with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
            validate_metadata_for_update(invalid_type)
        assert not isinstance(exc_info.value, InvalidMetadataFieldFormatError)
