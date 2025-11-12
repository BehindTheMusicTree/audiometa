import pytest

from audiometa import update_metadata
from audiometa.test.helpers.id3v2.id3v2_header_verifier import ID3v2HeaderVerifier
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestLyricsWriting:
    def test_id3v2_3_default_en(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_lyrics = "These are test lyrics\nWith multiple lines\nFor testing purposes"
            test_metadata = {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: test_lyrics}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0))

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert [f"eng\x00{test_lyrics}"] == raw_metadata["USLT"]

    def test_id3v2_4_default_en(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_lyrics = "These are test lyrics\nWith multiple lines\nFor testing purposes"
            test_metadata = {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: test_lyrics}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0))

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.4")
            assert [f"eng\x00{test_lyrics}"] == raw_metadata["USLT"]

    def test_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            test_lyrics = "RIFF test lyrics\nWith multiple lines\nFor testing purposes"
            test_metadata = {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: test_lyrics}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.RIFF)

            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert f"TAG:lyrics={test_lyrics}" in raw_metadata

    def test_vorbis(self):
        from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter

        with temp_file_with_metadata({}, "flac") as test_file:
            test_lyrics = "Vorbis test lyrics\nWith multiple lines\nFor testing purposes"
            test_metadata = {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: test_lyrics}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.VORBIS)

            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert f"LYRICS={test_lyrics}" in raw_metadata

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with temp_file_with_metadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: 12345}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file, bad_metadata)
