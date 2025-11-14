import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestGenreSmartReading:
    def test_single_entry_text_with_codes_and_separators_and_without_parentheses(self):
        """Test single genre entry with text with codes and separators without parentheses:

        '17/6' -> ['Rock', 'Grunge']
        """
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with text with codes and separators without parentheses
            ID3v2MetadataSetter.set_genres(test_file, ["17/6"], version="2.4")

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)
            assert genres == ["Rock", "Grunge"]

    def test_single_entry_codes_without_separators_id3v2(self):
        """Test single genre entry with codes without separators: '(17)(6)' -> ['Rock', 'Grunge']"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with codes without separators
            ID3v2MetadataSetter.set_genres(test_file, ["(17)(6)"], version="2.4")

            # Validate raw metadata
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert "(17)(6)" in raw_metadata["TCON"]

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock", "Grunge"]

    def test_single_entry_codes_without_separators_vorbis(self):
        """Test single genre entry with codes without separators in Vorbis: '(17)(6)' -> ['Rock', 'Grunge']"""
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            # Set genre with codes without separators
            VorbisMetadataSetter.set_genres(test_file, ["(17)(6)"])

            # Validate raw metadata
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "(17)(6)" in raw_metadata

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)
            assert genres == ["Rock", "Grunge"]

    def test_code_text_then_text_part_even_if_different(self):
        """Test code+text: '(17)Rock' -> 'Rock' (text part only)"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with code+text
            ID3v2MetadataSetter.set_genres(test_file, ["(17)Rock"], version="2.4")

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock"]

    def test_single_entry_code_text_without_separators(self):
        """Test single genre entry with code+text without separators: '(17)Rock(6)Blues' -> ['Rock', 'Grunge']"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with code+text without separators
            ID3v2MetadataSetter.set_genres(test_file, ["(17)Rock(6)Blues"], version="2.4")

            # Validate raw metadata
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert "(17)Rock(6)Blues" in raw_metadata["TCON"]

            # assert no null separators in raw metadata genre
            assert not any("\x00" in s for s in raw_metadata["TCON"])

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock", "Blues"]

    def test_one_code_and_one_code_text_in_single_entry(self):
        """Test one code and one code+text: '(17)', '(6)Grunge' -> ['Rock', 'Grunge']"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with one code and one code+text
            ID3v2MetadataSetter.set_genres(test_file, ["(17)(6)Grunge"], version="2.4")

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock", "Grunge"]

    def test_one_code_and_one_code_text_in_multi_entries(self):
        """Test one code and one code+text: '(17)', '(6)Grunge' -> ['Rock', 'Grunge']"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with one code and one code+text
            ID3v2MetadataSetter.set_genres(test_file, ["(17)", "(6)Grunge"], in_separate_frames=True, version="2.4")
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)

            assert "(17)" in raw_metadata["TCON"]
            assert "(6)Grunge" in raw_metadata["TCON"]

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock", "Grunge"]

    def test_single_entry_text_with_slash_separators(self):
        """Test single genre entry with text with slash separators: 'Rock/Blues' -> ['Rock', 'Blues']"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with text with separators
            ID3v2MetadataSetter.set_genres(test_file, ["Rock/Blues"], version="2.4")

            # Validate raw metadata
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert "Rock/Blues" in raw_metadata["TCON"]

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock", "Blues"]

    def test_single_entry_text_with_semicolon_separators(self):
        """Test single genre entry with text with semicolon separators:

        'Rock; Alternative' -> ['Rock', 'Alternative']
        """
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with text with separators
            ID3v2MetadataSetter.set_genres(test_file, ["Rock; Alternative"], version="2.4")

            # Validate raw metadata
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert "Rock; Alternative" in raw_metadata["TCON"]

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock", "Alternative"]

    def test_multi_codes_with_text_with_separators(self):
        """Test single genre entry with mixed separators: '(17)Rock/(6)Blues' -> ['Rock', 'Blues']"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with mixed separators
            ID3v2MetadataSetter.set_genres(test_file, ["(17)Rock/(6)Blues"], version="2.4")

            # Validate raw metadata
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert "(17)Rock/(6)Blues" in raw_metadata["TCON"]

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock", "Blues"]

    def test_multiple_entries_return_as_is(self):
        """Test multiple genre entries: separate TCON frames, return as-is without parsing."""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set multiple genres in separate frames
            ID3v2MetadataSetter.set_genres(test_file, ["Rock/Grunge", "Blues"], in_separate_frames=True, version="2.4")

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            # Should return as-is without parsing
            assert set(genres) == {"Rock/Grunge", "Blues"}

    def test_code_to_name_conversion_with_unknown_code(self):
        """Test code conversion: '(17)' -> 'Rock', (unknown code) -> unknown code in parentheses should be ignored."""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with known and unknown codes
            ID3v2MetadataSetter.set_genres(test_file, ["(17)", "(999)"], version="2.4")

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock"]

    def test_code_text_uses_text_part(self):
        """Test code+text: '(199)Rock' -> 'Rock' (text part only)"""
        with temp_file_with_metadata({"title": "Test Song"}, "id3v2.4") as test_file:
            # Set genre with code+text
            ID3v2MetadataSetter.set_genres(test_file, ["(199)Rock"], version="2.4")

            # Read via API
            genres = get_unified_metadata_field(test_file, UnifiedMetadataKey.GENRES_NAMES)

            assert genres == ["Rock"]
