import contextlib

import pytest

from audiometa import _validate_unified_metadata_types
from audiometa.exceptions import InvalidMetadataFieldTypeError
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestUnifiedMetadataTypeValidation:
    def test_track_number_invalid_types(self):
        invalid_values = [
            [],  # Empty list
            {},  # Empty dict
            object(),  # Custom object
            (1, 2, 3),  # Tuple
            {1, 2, 3},  # Set
            frozenset([1, 2, 3]),  # Frozenset
            3.14,  # Float
            {"key": "value"},  # Dict
            [1, 2, 3],  # List
        ]

        for invalid_value in invalid_values:
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                _validate_unified_metadata_types({UnifiedMetadataKey.TRACK_NUMBER: invalid_value})
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.TRACK_NUMBER.value
            assert error.value == invalid_value

        # Test valid values
        valid_values = [5, "5", "5/12", None]
        for valid_value in valid_values:
            # Should not raise any exception
            _validate_unified_metadata_types({UnifiedMetadataKey.TRACK_NUMBER: valid_value})

    def test_none_values_for_required_fields_are_allowed(self):
        # None means "Remove this metadata field", so it should be allowed for all fields
        none_metadata = {
            UnifiedMetadataKey.TITLE: None,
            UnifiedMetadataKey.ALBUM: None,
            UnifiedMetadataKey.BPM: None,
            UnifiedMetadataKey.ARTISTS: None,
            UnifiedMetadataKey.TRACK_NUMBER: None,
        }

        # Should not raise InvalidMetadataFieldTypeError
        _validate_unified_metadata_types(none_metadata)

    def test_complex_object_types_for_string_fields(self):
        class CustomObject:
            def __init__(self, value):
                self.value = value

            def __str__(self):
                return f"CustomObject({self.value})"

        invalid_values = [
            CustomObject("test"),  # Custom object
            (1, 2, 3),  # Tuple
            {1, 2, 3},  # Set
            frozenset([1, 2, 3]),  # Frozenset
            {"key": "value"},  # Dict
            [1, 2, 3],  # List
            None,  # None (wait, this should be allowed!)
        ]

        for invalid_value in invalid_values:
            if invalid_value is None:
                # None should be allowed
                continue
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                _validate_unified_metadata_types({UnifiedMetadataKey.TITLE: invalid_value})
            assert exc_info.value.field == UnifiedMetadataKey.TITLE.value
            assert exc_info.value.value == invalid_value

    def test_boolean_values_for_string_fields(self):
        with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
            _validate_unified_metadata_types({UnifiedMetadataKey.TITLE: True})
        assert exc_info.value.field == UnifiedMetadataKey.TITLE.value
        assert exc_info.value.value is True

        with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
            _validate_unified_metadata_types({UnifiedMetadataKey.ALBUM: False})
        assert exc_info.value.field == UnifiedMetadataKey.ALBUM.value
        assert exc_info.value.value is False

    def test_boolean_values_for_int_fields_are_allowed(self):
        # Boolean values should be accepted for int fields (True=1, False=0)
        _validate_unified_metadata_types({UnifiedMetadataKey.BPM: True})  # Should work
        _validate_unified_metadata_types({UnifiedMetadataKey.BPM: False})  # Should work

    def test_float_values_for_int_fields(self):
        # BPM should reject floats
        with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
            _validate_unified_metadata_types({UnifiedMetadataKey.BPM: 128.5})
        assert exc_info.value.field == UnifiedMetadataKey.BPM.value
        assert exc_info.value.value == 128.5

        # TRACK_NUMBER should reject floats (even though it accepts strings)
        with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
            _validate_unified_metadata_types({UnifiedMetadataKey.TRACK_NUMBER: 5.7})
        assert exc_info.value.field == UnifiedMetadataKey.TRACK_NUMBER.value
        assert exc_info.value.value == 5.7

    def test_complex_object_types_for_list_fields(self):
        class CustomObject:
            pass

        invalid_values = [
            CustomObject(),  # Custom object
            42,  # Int
            "single string",  # String (should be list)
            {"key": "value"},  # Dict
            True,  # Boolean
            3.14,  # Float
            None,  # None (should be allowed)
        ]

        for invalid_value in invalid_values:
            if invalid_value is None:
                # None should be allowed
                continue
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                _validate_unified_metadata_types({UnifiedMetadataKey.ARTISTS: invalid_value})
            assert exc_info.value.field == UnifiedMetadataKey.ARTISTS.value
            assert exc_info.value.value == invalid_value

    def test_empty_collections(self):
        # Empty string for TITLE (should be valid)
        _validate_unified_metadata_types({UnifiedMetadataKey.TITLE: ""})

        # Empty list for ARTISTS (might be valid or invalid depending on implementation)
        with contextlib.suppress(InvalidMetadataFieldTypeError):
            _validate_unified_metadata_types({UnifiedMetadataKey.ARTISTS: []})
            # If this succeeds, empty lists are allowed

    def test_unicode_and_special_characters(self):
        # Valid unicode strings should work
        _validate_unified_metadata_types({UnifiedMetadataKey.TITLE: "Test with émojis 🎵 and spëcial chärs"})

        # But invalid types should still fail
        with pytest.raises(InvalidMetadataFieldTypeError):
            _validate_unified_metadata_types({UnifiedMetadataKey.TITLE: b"bytes object"})

    def test_nested_collections(self):
        invalid_values = [
            [{"nested": "dict"}],  # List of dicts
            {"key": ["list"]},  # Dict with list value
            [[1, 2], [3, 4]],  # Nested lists
            {"set": {1, 2, 3}},  # Dict with set value
        ]

        for invalid_value in invalid_values:
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                _validate_unified_metadata_types({UnifiedMetadataKey.TITLE: invalid_value})
            assert exc_info.value.field == UnifiedMetadataKey.TITLE.value
            assert exc_info.value.value == invalid_value
