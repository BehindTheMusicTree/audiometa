import pytest
from unittest.mock import MagicMock

from audiometa.manager.MetadataManager import MetadataManager


@pytest.mark.unit
class TestSeparatorSelection:
    
    @pytest.mark.parametrize("values, expected_separator", [
        (["Artist One", "Artist Two"], "//"),
        (["Artist One", "Artist Two", "Artist Three"], "//"),
        (["Artist;One", "Artist;Two"], "//"),
        (["Artist,One", "Artist,Two"], "//"),
        (["Artist/One", "Artist/Two"], "//"),
        (["Artist\\One", "Artist\\Two"], "//"),
        (["Artist\\One", "Artist;Two"], "//"),
    ])
    def test_find_safe_separator(self, values, expected_separator):
        separator = MetadataManager.find_safe_separator(values)
        assert separator == expected_separator
        
        for value in values:
            assert separator not in value
    
    def test_find_safe_separator_no_safe_separator(self):
        # Test case where all common separators appear
        # Note: Single backslash is hard to test, so this tests the common separators
        from audiometa.manager.MetadataManager import METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED
        values = ["Artist//One", "Artist;Two", "Artist/Three", "Artist,Four"]
        separator = MetadataManager.find_safe_separator(values)
        # Should still find a safe separator (backslash-based ones don't appear)
        assert separator in METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED
        for value in values:
            assert separator not in value
    
    def test_find_safe_separator_empty_list(self):
        from audiometa.manager.MetadataManager import METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED
        separator = MetadataManager.find_safe_separator([])
        assert separator in METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED
    
    def test_find_safe_separator_single_value(self):
        separator = MetadataManager.find_safe_separator(["Artist One"])
        assert separator == "//"

