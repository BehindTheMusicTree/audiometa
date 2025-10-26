

import pytest

from audiometa import get_unified_metadata_field
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestCopyrightReading:
    def test_id3v1(self):
        with TempFileWithMetadata({"title": "Test Song"}, "id3v1") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError, match="UnifiedMetadataKey.COPYRIGHT metadata not supported by this format"):
                get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COPYRIGHT, metadata_format=MetadataFormat.ID3V1)

    def test_id3v2(self):
        with TempFileWithMetadata({"title": "Test Song", "copyright": "Test Copyright"}, "mp3") as test_file:
            copyright_info = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info == "Test Copyright"

    def test_vorbis(self):
        with TempFileWithMetadata({"title": "Test Song", "copyright": "Test Copyright"}, "flac") as test_file:
            copyright_info = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info == "Test Copyright"

    def test_riff(self):
        with TempFileWithMetadata({"title": "Test Song"}, "wav") as test_file:
            copyright_info = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info is None
