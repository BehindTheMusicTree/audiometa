import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.exceptions import MetadataFormatNotSupportedByAudioFormatError
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestMp3Writing:
    def test_writing_default_format_mp3(self):
        with TempFileWithMetadata({}, "mp3") as temp_mp3_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title Default"}
            update_metadata(temp_mp3_file, metadata)
            
            id3v2_title = ID3v2MetadataGetter.get_title(temp_mp3_file.path)
            assert id3v2_title == "Test Title Default"

    def test_id3v1_metadata_writing_mp3(self):
        with TempFileWithMetadata({}, "mp3") as temp_audio_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v1"}
            update_metadata(temp_audio_file, metadata, metadata_format=MetadataFormat.ID3V1)
            read_metadata = get_unified_metadata(temp_audio_file, metadata_format=MetadataFormat.ID3V1)
            assert read_metadata[UnifiedMetadataKey.TITLE] == "Test Title ID3v1"

    def test_id3v2_3_metadata_writing_mp3(self):
        with TempFileWithMetadata({}, "id3v2.3") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v2.3"}
            update_metadata(test_file.path, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0))
            read_metadata = get_unified_metadata(test_file.path, metadata_format=MetadataFormat.ID3V2)
            assert read_metadata[UnifiedMetadataKey.TITLE] == "Test Title ID3v2.3"
            
    def test_id3v2_4_metadata_writing_mp3(self):
        with TempFileWithMetadata({}, "id3v2.4") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v2.4"}
            update_metadata(test_file.path, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0))
            read_metadata = get_unified_metadata(test_file.path, metadata_format=MetadataFormat.ID3V2)
            assert read_metadata[UnifiedMetadataKey.TITLE] == "Test Title ID3v2.4"
            
    def test_riff_metadata_writing_mp3(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataFormatNotSupportedByAudioFormatError):
                update_metadata(test_file.path, {UnifiedMetadataKey.TITLE: "Test Title RIFF"}, metadata_format=MetadataFormat.RIFF)
                
                
    def test_vorbis_metadata_writing_mp3(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataFormatNotSupportedByAudioFormatError):
                update_metadata(test_file.path, {UnifiedMetadataKey.TITLE: "Test Title Vorbis"}, metadata_format=MetadataFormat.VORBIS)