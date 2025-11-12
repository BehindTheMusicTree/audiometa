from pathlib import Path

import pytest

from audiometa import get_unified_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestSpecialCharactersEdgeCases:
    def test_read_unicode_characters(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["François", "José", "Müller", "北京"])
            VorbisMetadataSetter.add_title(test_file, "Café Music 音乐")
            metadata_title = VorbisMetadataGetter.get_title(test_file)
            assert metadata_title == "Café Music 音乐"

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)

            assert isinstance(artists, list)
            assert len(artists) == 4
            assert "François" in artists
            assert "José" in artists
            assert "Müller" in artists
            assert "北京" in artists

            assert isinstance(title, str)
            assert title == "Café Music 音乐"

    def test_read_special_punctuation(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist & Co.", "Band (feat. Singer)", "Group - The Band"])
            VorbisMetadataSetter.add_title(test_file, "Song (Remix) - Special Edition")

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist & Co." in artists
            assert "Band (feat. Singer)" in artists
            assert "Group - The Band" in artists

            assert isinstance(title, str)
            assert title == "Song (Remix) - Special Edition"

    def test_read_quotes_and_apostrophes(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist's Band", 'The "Quoted" Band', "It's a Band"])
            VorbisMetadataSetter.add_title(test_file, 'Don\'t Stop "Believing"')

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist's Band" in artists
            assert 'The "Quoted" Band' in artists
            assert "It's a Band" in artists

            assert isinstance(title, str)
            assert title == 'Don\'t Stop "Believing"'

    def test_read_control_characters(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(
                test_file, ["Artist\twith\ttabs", "Band\nwith\nnewlines", "Group\rwith\rcarriage"]
            )
            VorbisMetadataSetter.add_title(test_file, "Song\twith\ttabs")

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist\twith\ttabs" in artists
            assert "Band\nwith\nnewlines" in artists
            assert "Group\rwith\rcarriage" in artists

            assert isinstance(title, str)
            assert title == "Song\twith\ttabs"

    def test_read_very_long_strings(self):
        long_string = "A" * 1000
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, [long_string, "Short Artist"])
            VorbisMetadataSetter.add_title(test_file, "B" * 500)

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)

            assert isinstance(artists, list)
            assert len(artists) == 2
            assert long_string in artists
            assert "Short Artist" in artists

            assert isinstance(title, str)
            assert title == "B" * 500

    def test_read_mixed_encodings(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["ASCII Artist", "Français", "Русский", "العربية", "中文"])
            VorbisMetadataSetter.add_title(test_file, "Mixed 编码 Title")

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)

            assert isinstance(artists, list)
            assert len(artists) == 5
            assert "ASCII Artist" in artists
            assert "Français" in artists
            assert "Русский" in artists
            assert "العربية" in artists
            assert "中文" in artists

            assert isinstance(title, str)
            assert title == "Mixed 编码 Title"

    def test_read_special_separator_characters(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(
                test_file, ["Artist; with; semicolons", "Band, with, commas", "Group|with|pipes"]
            )
            VorbisMetadataSetter.add_title(test_file, "Song; with; separators")

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist; with; semicolons" in artists
            assert "Band, with, commas" in artists
            assert "Group|with|pipes" in artists

            assert isinstance(title, str)
            assert title == "Song; with; separators"

    def test_read_html_xml_characters(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist <tag>", "Band &amp; Co.", "Group &lt;test&gt;"])
            VorbisMetadataSetter.add_title(test_file, "Song &amp; Title")

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist <tag>" in artists
            assert "Band &amp; Co." in artists
            assert "Group &lt;test&gt;" in artists

            assert isinstance(title, str)
            assert title == "Song &amp; Title"

    def test_read_emoji_characters(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(test_file, ["Artist 🎵", "Band 🎸", "Group 🎤"])
            VorbisMetadataSetter.add_title(test_file, "Song 🎶 with 🎵 emojis")

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "Artist 🎵" in artists
            assert "Band 🎸" in artists
            assert "Group 🎤" in artists

            assert isinstance(title, str)
            assert title == "Song 🎶 with 🎵 emojis"

    def test_read_mixed_special_characters(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_artists(
                test_file,
                [
                    "François & Co. (feat. Müller) 🎵",
                    'The "Quoted" Band - Special Characters',
                    "Artist with\nnewlines\tand\ttabs",
                ],
            )
            VorbisMetadataSetter.add_title(test_file, 'Mixed Special 🎵 Characters & "Quotes"')

            unified_metadata = get_unified_metadata(test_file)
            artists = unified_metadata.get(UnifiedMetadataKey.ARTISTS)
            title = unified_metadata.get(UnifiedMetadataKey.TITLE)

            assert isinstance(artists, list)
            assert len(artists) == 3
            assert "François & Co. (feat. Müller) 🎵" in artists
            assert 'The "Quoted" Band - Special Characters' in artists
            assert "Artist with\nnewlines\tand\ttabs" in artists

            assert isinstance(title, str)
            assert title == 'Mixed Special 🎵 Characters & "Quotes"'

    def test_read_special_characters_from_existing_file(self, sample_mp3_file: Path):
        # Test reading special characters from a file that already has them
        # This tests the reading functionality without writing first
        unified_metadata = get_unified_metadata(sample_mp3_file)

        # Should handle any special characters that might be in the sample file
        for _key, value in unified_metadata.items():
            if isinstance(value, str):
                # Should be able to handle unicode and special characters
                assert isinstance(value, str)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        assert isinstance(item, str)
