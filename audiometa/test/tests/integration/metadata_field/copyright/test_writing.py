import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestCopyrightWriting:
    def test_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_copyright = "© 2024 Test Label ID3v2"
            test_metadata = {UnifiedMetadataKey.COPYRIGHT: test_copyright}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2)
            copyright_info = get_unified_metadata_field(test_file, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info == test_copyright

    def test_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            test_copyright = "© 2024 Test Label RIFF"
            test_metadata = {UnifiedMetadataKey.COPYRIGHT: test_copyright}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.RIFF)
            copyright_info = get_unified_metadata_field(test_file, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info == test_copyright

    def test_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            test_copyright = "© 2024 Test Label Vorbis"
            test_metadata = {UnifiedMetadataKey.COPYRIGHT: test_copyright}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.VORBIS)
            copyright_info = get_unified_metadata_field(test_file, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info == test_copyright

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with temp_file_with_metadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.COPYRIGHT: 123}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file, bad_metadata)
