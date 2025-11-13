import pytest

from audiometa import get_unified_metadata_field
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestCopyrightReading:
    def test_id3v1(self):
        with (
            temp_file_with_metadata({"title": "Test Song"}, "id3v1") as test_file,
            pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.COPYRIGHT metadata not supported by ID3v1 format",
            ),
        ):
            get_unified_metadata_field(test_file, UnifiedMetadataKey.COPYRIGHT, metadata_format=MetadataFormat.ID3V1)

    def test_id3v2(self):
        with temp_file_with_metadata({"title": "Test Song", "copyright": "Test Copyright"}, "mp3") as test_file:
            copyright_info = get_unified_metadata_field(test_file, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info == "Test Copyright"

    def test_vorbis(self):
        with temp_file_with_metadata({"title": "Test Song", "copyright": "Test Copyright"}, "flac") as test_file:
            copyright_info = get_unified_metadata_field(test_file, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info == "Test Copyright"

    def test_riff(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            copyright_info = get_unified_metadata_field(test_file, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info is None
