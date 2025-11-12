import pytest

from audiometa import get_unified_metadata
from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestMultipleMetadata:
    def test_id3v1(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            # First set ID3v1 metadata using external tools
            ID3v1MetadataSetter.set_title(test_file, "ID3v1 Title")
            ID3v1MetadataSetter.set_artist(test_file, "ID3v1 Artist")
            ID3v1MetadataSetter.set_album(test_file, "ID3v1 Album")

            merged_metadata = get_unified_metadata(test_file)
            assert merged_metadata.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"
            assert merged_metadata.get(UnifiedMetadataKey.ARTISTS) == ["ID3v1 Artist"]
            assert merged_metadata.get(UnifiedMetadataKey.ALBUM) == "ID3v1 Album"

    def test_id3v2_3(self):
        with temp_file_with_metadata({}, "id3v2.3") as test_file:
            # First set ID3v2.3 metadata using external tools
            ID3v2MetadataSetter.set_title(test_file, "ID3v2.3 Title", version="2.3")
            ID3v2MetadataSetter.set_artists(test_file, "ID3v2.3 Artist", version="2.3")
            ID3v2MetadataSetter.set_album(test_file, "ID3v2.3 Album", version="2.3")

            merged_metadata = get_unified_metadata(test_file)
            assert merged_metadata.get(UnifiedMetadataKey.TITLE) == "ID3v2.3 Title"
            assert merged_metadata.get(UnifiedMetadataKey.ARTISTS) == ["ID3v2.3 Artist"]
            assert merged_metadata.get(UnifiedMetadataKey.ALBUM) == "ID3v2.3 Album"

    def test_id3v2_4(self):
        with temp_file_with_metadata({}, "id3v2.4") as test_file:
            # First set ID3v2.4 metadata using external tools
            ID3v2MetadataSetter.set_title(test_file, "ID3v2.4 Title", version="2.4")
            ID3v2MetadataSetter.set_artists(test_file, "ID3v2.4 Artist", version="2.4")
            ID3v2MetadataSetter.set_album(test_file, "ID3v2.4 Album", version="2.4")

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.4")
            assert raw_metadata["TIT2"] == ["ID3v2.4 Title"]
            assert raw_metadata["TPE1"] == ["ID3v2.4 Artist"]
            assert raw_metadata["TALB"] == ["ID3v2.4 Album"]

            merged_metadata = get_unified_metadata(test_file)
            assert merged_metadata.get(UnifiedMetadataKey.TITLE) == "ID3v2.4 Title"
            assert merged_metadata.get(UnifiedMetadataKey.ARTISTS) == ["ID3v2.4 Artist"]
            assert merged_metadata.get(UnifiedMetadataKey.ALBUM) == "ID3v2.4 Album"

    def test_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            # First set RIFF metadata using external tools
            from audiometa.test.helpers.riff import RIFFMetadataSetter

            RIFFMetadataSetter.set_title(test_file, "RIFF Title")
            RIFFMetadataSetter.set_artist(test_file, "RIFF Artist")
            RIFFMetadataSetter.set_album(test_file, "RIFF Album")

            merged_metadata = get_unified_metadata(test_file)
            assert merged_metadata.get(UnifiedMetadataKey.TITLE) == "RIFF Title"
            assert merged_metadata.get(UnifiedMetadataKey.ARTISTS) == ["RIFF Artist"]
            assert merged_metadata.get(UnifiedMetadataKey.ALBUM) == "RIFF Album"

    def test_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            # First set Vorbis metadata using external tools
            from audiometa.test.helpers.vorbis import VorbisMetadataSetter

            VorbisMetadataSetter.add_title(test_file, "Vorbis Title")
            VorbisMetadataSetter.set_artist(test_file, "Vorbis Artist")
            VorbisMetadataSetter.set_album(test_file, "Vorbis Album")

            merged_metadata = get_unified_metadata(test_file)
            assert merged_metadata.get(UnifiedMetadataKey.TITLE) == "Vorbis Title"
            assert merged_metadata.get(UnifiedMetadataKey.ARTISTS) == ["Vorbis Artist"]
            assert merged_metadata.get(UnifiedMetadataKey.ALBUM) == "Vorbis Album"
