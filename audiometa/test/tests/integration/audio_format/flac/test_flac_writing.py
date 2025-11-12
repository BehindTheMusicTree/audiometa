import pytest

from audiometa import update_metadata
from audiometa.exceptions import MetadataFormatNotSupportedByAudioFormatError
from audiometa.test.helpers.id3v1.id3v1_metadata_getter import ID3v1MetadataGetter
from audiometa.test.helpers.id3v2.id3v2_header_verifier import ID3v2HeaderVerifier
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestFlacWriting:
    def test_writing_default_format_flac(self):
        with temp_file_with_metadata({}, "flac") as temp_flac_file_path:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title Default"}
            update_metadata(temp_flac_file_path, metadata)

            vorbis_title = VorbisMetadataGetter.get_title(temp_flac_file_path)
            assert vorbis_title == "Test Title Default"

    def test_vorbis_metadata_writing_flac(self):
        with temp_file_with_metadata({}, "flac") as temp_flac_file_path:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title Vorbis"}
            update_metadata(temp_flac_file_path, metadata, metadata_format=MetadataFormat.VORBIS)
            title = VorbisMetadataGetter.get_title(temp_flac_file_path)
            assert title == "Test Title Vorbis"

    def test_id3v2_3_metadata_writing_flac(self):
        with temp_file_with_metadata({}, "flac") as temp_flac_file_path:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v2.3"}
            update_metadata(
                temp_flac_file_path, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0)
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(temp_flac_file_path) == (2, 3, 0)

            title = ID3v2MetadataGetter.get_title(temp_flac_file_path)
            assert title == "Test Title ID3v2.3"

    def test_id3v2_4_metadata_writing_flac(self):
        with temp_file_with_metadata({}, "flac") as temp_flac_file_path:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v2.4"}
            update_metadata(
                temp_flac_file_path, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0)
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(temp_flac_file_path) == (2, 4, 0)

            title = ID3v2MetadataGetter.get_title(temp_flac_file_path)
            assert title == "Test Title ID3v2.4"

    def test_id3v1_metadata_writing_flac(self):
        with temp_file_with_metadata({}, "flac") as temp_flac_file_path:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v1"}
            update_metadata(temp_flac_file_path, metadata, metadata_format=MetadataFormat.ID3V1)
            title = ID3v1MetadataGetter.get_title(temp_flac_file_path)
            assert title == "Test Title ID3v1"

    def test_riff_metadata_writing_flac(self):
        with (
            temp_file_with_metadata({}, "flac") as test_file,
            pytest.raises(MetadataFormatNotSupportedByAudioFormatError),
        ):
            update_metadata(
                test_file, {UnifiedMetadataKey.TITLE: "Test Title RIFF"}, metadata_format=MetadataFormat.RIFF
            )
