import pytest

from audiometa.manager._MetadataManager import _MetadataManager as MetadataManager


@pytest.mark.unit
class TestSeparatorSelection:
    @pytest.mark.parametrize(
        ("values", "expected_separator"),
        [
            (["Artist One", "Artist Two"], "//"),
            (["Artist One", "Artist Two", "Artist Three"], "//"),
            (["Artist;One", "Artist;Two"], "//"),
            (["Artist,One", "Artist,Two"], "//"),
            (["Artist/One", "Artist/Two"], "//"),
            (["Artist\\One", "Artist\\Two"], "//"),
            (["Artist\\One", "Artist;Two"], "//"),
            # Cases where // is present, so pick \\\\
            (["Artist//One", "Artist Two"], "\\\\"),
            (["Artist//One", "Artist//Two"], "\\\\"),
            # Cases where // and \\\\ are present, so pick ;
            (["Artist//One", "Artist\\\\Two"], ";"),
            (["Artist//One", "Artist\\\\Two", "Artist\\Three"], ";"),
            # Cases where //, \\\\, \\, ; are present, so pick ,
            (["Artist//One", "Artist\\\\Two", "Artist\\Three", "Artist;Four"], ","),
            (["Artist//One", "Artist\\\\Two", "Artist\\Three", "Artist;Four", "Artist/Five"], ","),
            # Cases with mixed separators
            (["Artist;One", "Artist,Two", "Artist/Three"], "//"),
            (["Artist\\One", "Artist;Two", "Artist,Three"], "//"),
            (["Artist/One", "Artist,Two"], "//"),
            # Edge cases
            (["Artist//One;Two", "Artist Three"], "\\\\"),
            (["Artist\\\\One\\Two", "Artist;Three"], "//"),
        ],
    )
    def test_find_safe_separator(self, values, expected_separator):
        separator = MetadataManager.find_safe_separator(values)
        assert separator == expected_separator

        for value in values:
            assert separator not in value

    def test_find_safe_separator_prioritizes_highest_available(self):
        # When clean values, uses highest priority
        values = ["Artist One", "Artist Two"]
        separator = MetadataManager.find_safe_separator(values)
        assert separator == "//"

        # When // appears, uses next priority
        values = ["Artist//One", "Artist Two"]
        separator = MetadataManager.find_safe_separator(values)
        assert separator == "\\\\"  # Double backslash

        # When both // and \\ appear, uses semicolon
        values = ["Artist//One", "Artist\\\\Two"]  # Note: \\\\ in string is \\
        separator = MetadataManager.find_safe_separator(values)
        assert separator not in ["//", "\\"]  # Neither // nor single \
        for value in values:
            assert separator not in value

    def test_find_safe_separator_no_safe_separator(self):
        # Test case where all common separators appear
        # Note: Single backslash is hard to test, so this tests the common separators
        from audiometa.manager._MetadataManager import METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED

        values = ["Artist//One", "Artist;Two", "Artist/Three", "Artist,Four"]
        separator = MetadataManager.find_safe_separator(values)
        # Should still find a safe separator (backslash-based ones don't appear)
        assert separator in METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED
        for value in values:
            assert separator not in value

    @pytest.mark.parametrize(
        "values",
        [
            (["Artist//One", "Artist\\\\Two"]),
            (["Artist;One", "Artist\\Two", "Artist,Three"]),
            (["Band/Name", "Artist;Separated", "Composer,List"]),
            (["Artist//With\\Slashes", "Another;With\\Semicolon"]),
        ],
    )
    def test_real_world_artist_names(self, values):
        separator = MetadataManager.find_safe_separator(values)
        for value in values:
            assert separator not in value

    def test_values_with_multiple_separators(self):
        values = ["Artist//One/Two", "Artist\\\\Three\\Four", "Artist;Five"]
        separator = MetadataManager.find_safe_separator(values)
        # Should find a separator that's safe (doesn't appear in values)
        # Since all common separators appear, it will pick the last available one
        for value in values:
            assert separator not in value

    def test_empty_list(self):
        from audiometa.manager._MetadataManager import METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED

        separator = MetadataManager.find_safe_separator([])
        assert separator in METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED

    def test_single_value(self):
        separator = MetadataManager.find_safe_separator(["Artist One"])
        assert separator == "//"

    @pytest.mark.parametrize(
        ("values", "expected_separator"),
        [
            (["DJ Snake", "The Chainsmokers"], "//"),
            (["Miley Cyrus & Billy Ray Cyrus", "Florida Georgia Line"], "//"),
            (["Hank Williams, Jr", "Hank Williams"], "//"),
            # // and / appear, so skips to \\\\
            (["7//Heaven", "Back/Street"], "\\\\"),
            # ; and \ appear, so skips to //
            (["Artist;With\\Backslash", "Another\\Artist"], "//"),
        ],
    )
    def test_complex_artist_names_from_spec_examples(self, values, expected_separator):
        separator = MetadataManager.find_safe_separator(values)
        assert separator == expected_separator
        for value in values:
            assert separator not in value

    def test_unicode_and_special_characters(self):
        values = ["Artíst", "Artišt", "Arti§t"]
        separator = MetadataManager.find_safe_separator(values)
        assert separator == "//"

    def test_spaces_and_punctuation(self):
        values = ["Artist One (Feat. Collaborator)", "Artist Two & Friend"]
        separator = MetadataManager.find_safe_separator(values)
        assert separator == "//"

    def test_find_safe_separator_empty_and_whitespace_values(self):
        """Test behavior with empty strings and whitespace."""
        values = ["", "   ", "Artist One", "Artist Two"]
        separator = MetadataManager.find_safe_separator(values)
        assert separator == "//"

        # Empty and whitespace shouldn't affect separator choice
        for value in values:
            if value.strip():  # Only check non-empty values
                assert separator not in value
