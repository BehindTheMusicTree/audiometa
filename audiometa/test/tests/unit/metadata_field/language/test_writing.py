
import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter


@pytest.mark.integration
class TestLanguageWriting:
    def test_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            test_language = "en"
            test_metadata = {UnifiedMetadataKey.LANGUAGE: test_language}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            language = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.LANGUAGE)
            assert language == test_language

    def test_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            test_language = "fr"
            test_metadata = {UnifiedMetadataKey.LANGUAGE: test_language}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.RIFF)
            
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file.path)
            assert "TAG:language=fr" in raw_metadata

    def test_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            test_language = "de"
            test_metadata = {UnifiedMetadataKey.LANGUAGE: test_language}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.VORBIS)
            language = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.LANGUAGE)
            assert language == test_language

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with TempFileWithMetadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.LANGUAGE: 123}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file.path, bad_metadata)
