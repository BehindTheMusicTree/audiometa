import pytest

from audiometa import update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestLyricsDeleting:
    def test_delete_lyrics_id3v1(self):
        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS metadata not supported by ID3v1 format",
            ),
        ):
            update_metadata(
                test_file,
                {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: "Test lyrics"},
                metadata_format=MetadataFormat.ID3V1,
            )

    def test_delete_lyrics_id3v2_3(self):
        with temp_file_with_metadata({}, "id3v2.3") as test_file:
            ID3v2MetadataSetter.set_lyrics(test_file, "Test lyrics", version="2.3")
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            # 4 null bytes because of missing language
            assert raw_metadata["USLT"] == ["\x00\x00\x00\x00Test lyrics"]

            update_metadata(
                test_file,
                {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None},
                metadata_format=MetadataFormat.ID3V2,
                id3v2_version=(2, 3, 0),
            )

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert raw_metadata.get("USLT") is None

    def test_delete_lyrics_id3v2_4(self):
        with temp_file_with_metadata({}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_lyrics(test_file, "Test lyrics", version="2.4")
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.4")
            assert raw_metadata["USLT"] == ["eng\x00Test lyrics"]

            update_metadata(
                test_file,
                {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None},
                metadata_format=MetadataFormat.ID3V2,
                id3v2_version=(2, 4, 0),
            )

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.4")
            assert raw_metadata.get("USLT") is None

    def test_delete_lyrics_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
            from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter

            RIFFMetadataSetter.set_lyrics(test_file, "Test lyrics")
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "TAG:lyrics=Test lyrics" in raw_metadata

            update_metadata(
                test_file, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.RIFF
            )

            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "TAG:lyrics=" not in raw_metadata

    def test_delete_lyrics_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter

            VorbisMetadataSetter.set_lyrics(test_file, "Test lyrics")
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "LYRICS=Test lyrics" in raw_metadata

            update_metadata(
                test_file, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.VORBIS
            )

            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "LYRICS=" not in raw_metadata

    def test_delete_lyrics_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Set multiple metadata fields using helper methods
            ID3v2MetadataSetter.set_lyrics(test_file, "Test lyrics")
            ID3v2MetadataSetter.set_title(test_file, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file, "Test Artist")

            # Delete only lyrics using library API
            update_metadata(
                test_file, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.ID3V2
            )

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata is None

    def test_delete_lyrics_already_none(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            # Try to delete lyrics that don't exist
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "LYRICS=" not in raw_metadata

            update_metadata(
                test_file, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.VORBIS
            )

            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "LYRICS=" not in raw_metadata

    def test_delete_lyrics_empty_string(self):
        from audiometa import get_unified_metadata_field

        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: ""}, metadata_format=MetadataFormat.ID3V2
            )
            lyrics = get_unified_metadata_field(test_file, UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS)
            assert lyrics is None
