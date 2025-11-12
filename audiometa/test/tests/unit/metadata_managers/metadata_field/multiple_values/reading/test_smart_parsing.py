from unittest.mock import MagicMock

import pytest

from audiometa.manager._MetadataManager import _MetadataManager as MetadataManager


@pytest.mark.unit
class TestSmartParsing:
    @pytest.mark.parametrize(
        ("values", "expected_should_parse"),
        [
            ([], False),
            ([""], False),
            ([" "], False),
            (["Artist One;Artist Two"], True),
            (["Artist One", "Artist Two"], False),
            (["Artist One//Artist Two"], True),
        ],
    )
    def test_should_apply_smart_parsing(self, values, expected_should_parse):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        result = manager._should_apply_smart_parsing(values)
        assert result == expected_should_parse

    def test_should_apply_smart_parsing_with_null_separators(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        result = manager._should_apply_smart_parsing(["Artist\x00One"])
        assert result is True

        result = manager._should_apply_smart_parsing(["Artist One", "Artist\x00Two"])
        assert result is True

    @pytest.mark.parametrize(
        ("values", "expected_parsed"),
        [
            (["Artist One;Artist Two"], ["Artist One", "Artist Two"]),
            (["Artist One//Artist Two"], ["Artist One", "Artist Two"]),
            (["Artist One,Artist Two"], ["Artist One", "Artist Two"]),
            (["Artist One\\Artist Two"], ["Artist One", "Artist Two"]),
            (["Artist One/Artist Two"], ["Artist One", "Artist Two"]),
            (["Artist One;Artist;Three"], ["Artist One", "Artist", "Three"]),
            (["Artist One;Artist Two;Artist Three"], ["Artist One", "Artist Two", "Artist Three"]),
            (["  Artist One  "], ["Artist One"]),
            ([""], []),
            (["  "], []),
            (["Artist One"], ["Artist One"]),
        ],
    )
    def test_apply_smart_parsing(self, values, expected_parsed):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        result = manager._apply_smart_parsing(values)
        assert result == expected_parsed

    def test_apply_smart_parsing_with_null_separators(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        result = manager._apply_smart_parsing(["Artist\x00One\x00Two"])
        assert result == ["Artist", "One", "Two"]

    def test_apply_smart_parsing_mixed_null_and_regular_separators(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        # Null separators take priority - split on null first
        result = manager._apply_smart_parsing(["Artist\x00One;Two"])
        assert result == ["Artist", "One;Two"]

    def test_apply_smart_parsing_multiple_entries_no_separators(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        # Multiple entries without separators - only first non-empty entry is parsed
        # This is because _apply_smart_parsing is designed for single-entry legacy data
        result = manager._apply_smart_parsing(["Artist One", "Artist Two"])
        assert result == ["Artist One"]

    def test_apply_smart_parsing_separator_priority_semicolon_over_comma(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        result = manager._apply_smart_parsing(["Artist One;Artist Two,Artist Three"])
        assert result == ["Artist One", "Artist Two,Artist Three"]

    def test_apply_smart_parsing_separator_priority_double_slash_over_slash(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        result = manager._apply_smart_parsing(["Artist One//Artist Two/Artist Three"])
        assert result == ["Artist One", "Artist Two/Artist Three"]

    def test_unicode_characters(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        # Unicode characters in parsed values
        values = ["Artist Café"]
        result = manager._apply_smart_parsing(values)
        assert "Artist Café" in result

    def test_empty_values_after_separation(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        result = manager._apply_smart_parsing(["Artist One;;Artist Two;"])
        assert result == ["Artist One", "Artist Two"]

    def test_whitespace_around_separators(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        result = manager._apply_smart_parsing(["Artist One ; Artist Two ; Artist Three"])
        assert result == ["Artist One", "Artist Two", "Artist Three"]

    def test_numeric_entries_in_parsed_value(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        values = ["Artist 1;Artist 2;123"]
        result = manager._apply_smart_parsing(values)
        assert "Artist 1" in result
        assert "Artist 2" in result
        assert "123" in result

    def test_case_sensitivity_in_parsed_value(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        values = ["Artist One;ARTIST TWO;artist three;ArTiSt FoUr"]
        result = manager._apply_smart_parsing(values)
        assert "Artist One" in result
        assert "ARTIST TWO" in result
        assert "artist three" in result
        assert "ArTiSt FoUr" in result

    def test_duplicate_entries_in_parsed_value(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        values = ["Artist One;Artist Two;Artist One;Artist Three;Artist Two"]
        result = manager._apply_smart_parsing(values)
        assert result.count("Artist One") == 2
        assert result.count("Artist Two") == 2
        assert result.count("Artist Three") == 1

    def test_order_preservation_in_parsed_value(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        values = ["First Artist;Second Artist;Third Artist;Fourth Artist"]
        result = manager._apply_smart_parsing(values)
        assert result[0] == "First Artist"
        assert result[1] == "Second Artist"
        assert result[2] == "Third Artist"
        assert result[3] == "Fourth Artist"

    def test_very_long_single_entry(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        long_artist = "A" * 10000
        result = manager._apply_smart_parsing([long_artist])
        assert result == [long_artist]
        assert len(result[0]) == 10000

    def test_mixed_empty_values_with_separators(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        result = manager._apply_smart_parsing(["Artist One;;;Artist Two;Artist;"])
        assert result == ["Artist One", "Artist Two", "Artist"]

    def test_multiple_spaces_within_values_preserved(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})

        values = ["Artist  One"]
        result = manager._apply_smart_parsing(values)
        assert "Artist  One" in result
