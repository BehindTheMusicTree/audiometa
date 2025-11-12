import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.exceptions import MetadataFormatNotSupportedByAudioFormatError
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestMp3Writing:
    def test_writing_default_format_mp3(self):
        with temp_file_with_metadata({}, "mp3") as temp_mp3_file_path:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title Default"}
            update_metadata(temp_mp3_file_path, metadata)

            id3v2_title = ID3v2MetadataGetter.get_title(temp_mp3_file_path)
            assert id3v2_title == "Test Title Default"

    def test_id3v1_metadata_writing_mp3(self):
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v1"}
            update_metadata(temp_audio_file_path, metadata, metadata_format=MetadataFormat.ID3V1)
            read_metadata = get_unified_metadata(temp_audio_file_path, metadata_format=MetadataFormat.ID3V1)
            assert read_metadata[UnifiedMetadataKey.TITLE] == "Test Title ID3v1"

    def test_id3v2_3_metadata_writing_mp3(self):
        with temp_file_with_metadata({}, "id3v2.3") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v2.3"}
            update_metadata(test_file, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0))
            read_metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert read_metadata[UnifiedMetadataKey.TITLE] == "Test Title ID3v2.3"

    def test_id3v2_4_metadata_writing_mp3(self):
        with temp_file_with_metadata({}, "id3v2.4") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v2.4"}
            update_metadata(test_file, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0))
            read_metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert read_metadata[UnifiedMetadataKey.TITLE] == "Test Title ID3v2.4"

    def test_riff_metadata_writing_mp3(self):
        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(MetadataFormatNotSupportedByAudioFormatError),
        ):
            update_metadata(
                test_file, {UnifiedMetadataKey.TITLE: "Test Title RIFF"}, metadata_format=MetadataFormat.RIFF
            )

    def test_vorbis_metadata_writing_mp3(self):
        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(MetadataFormatNotSupportedByAudioFormatError),
        ):
            update_metadata(
                test_file,
                {UnifiedMetadataKey.TITLE: "Test Title Vorbis"},
                metadata_format=MetadataFormat.VORBIS,
            )
