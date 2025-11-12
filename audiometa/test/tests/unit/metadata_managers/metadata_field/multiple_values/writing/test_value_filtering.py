import pytest

from audiometa.manager._MetadataManager import _MetadataManager as MetadataManager


@pytest.mark.unit
class TestValueFiltering:
    @pytest.mark.parametrize(
        ("values", "expected_filtered"),
        [
            (["Artist One", "Artist Two"], ["Artist One", "Artist Two"]),
            (["Artist One", ""], ["Artist One"]),
            (["Artist One", "  "], ["Artist One", "  "]),
            (["", "Artist Two"], ["Artist Two"]),
            ([None, "Artist Two"], ["Artist Two"]),
            (["Artist One", None, "Artist Two"], ["Artist One", "Artist Two"]),
            ([], []),
            ([""], []),
            (["  "], ["  "]),
            ([None], []),
            (["", None, "  "], ["  "]),
        ],
    )
    def test_filter_valid_values(self, values, expected_filtered):
        result = MetadataManager._filter_valid_values(values)
        assert result == expected_filtered

    def test_filter_valid_values_all_valid(self):
        values = ["Artist One", "Artist Two", "Artist Three"]
        result = MetadataManager._filter_valid_values(values)
        assert result == values

    def test_filter_valid_values_all_invalid(self):
        values = [None, ""]
        result = MetadataManager._filter_valid_values(values)
        assert result == []

    def test_mixed_empty_and_valid_entries_filtering(self):
        values = ["Valid Artist 1", "", "Valid Artist 2", "", "Valid Artist 3"]
        result = MetadataManager._filter_valid_values(values)
        assert result == ["Valid Artist 1", "Valid Artist 2", "Valid Artist 3"]

    def test_filter_valid_values_removes_empty_strings(self):
        values = ["Valid Artist", "", "Another Valid Artist"]
        result = MetadataManager._filter_valid_values(values)
        assert result == ["Valid Artist", "Another Valid Artist"]

    def test_filter_valid_values_only_whitespace_not_empty(self):
        # filter_valid_values only removes None and empty strings, not whitespace
        values = ["   ", "\t", "\n"]
        result = MetadataManager._filter_valid_values(values)
        assert result == values  # Whitespace strings are not empty

    def test_single_empty_value(self):
        values = [""]
        result = MetadataManager._filter_valid_values(values)
        assert result == []

    def test_none_and_empty_mixed(self):
        values = [None, "Artist", "", "Another Artist", None]
        result = MetadataManager._filter_valid_values(values)
        assert result == ["Artist", "Another Artist"]

    def test_all_none_values_filtered_to_empty_list(self):
        # Test that [None, None] filters to empty list
        # This matches the integration test scenario where field is removed
        values = [None, None]
        result = MetadataManager._filter_valid_values(values)
        assert result == []

    def test_mixed_none_and_valid_values_filtering(self):
        # Test that None values are filtered but valid values remain
        # This matches the integration test scenario
        values = ["Artist One", None, "Artist Two", None, "Artist Three"]
        result = MetadataManager._filter_valid_values(values)
        assert result == ["Artist One", "Artist Two", "Artist Three"]
