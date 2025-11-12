import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v1.id3v1_metadata_setter import ID3v1MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestId3v1:
    def test_semicolon_separated_artists(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v1MetadataSetter.set_artist(test_file, "Artist One;Artist Two")

            artists = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V1
            )

            assert isinstance(artists, list)
            assert len(artists) == 2
            assert "Artist One" in artists
            assert "Artist Two" in artists
