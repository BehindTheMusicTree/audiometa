import pytest

from audiometa.exceptions import InvalidMetadataFieldTypeError


@pytest.mark.unit
class TestExceptionClasses:
    def test_invalid_metadata_field_type_error_attributes(self):
        error = InvalidMetadataFieldTypeError("title", "str", 123)
        assert error.field == "title"
        assert error.expected_type == "str"
        assert error.actual_type == "int"
        assert error.value == 123
        assert isinstance(error, TypeError)

    def test_invalid_metadata_field_type_error_message_format(self):
        error = InvalidMetadataFieldTypeError("artists", "list[str]", {"key": "value"})
        message = str(error)
        assert "artists" in message
        assert "list[str]" in message
        assert "dict" in message or "actual_type" in message
        assert "'artists'" in message or "artists" in message
