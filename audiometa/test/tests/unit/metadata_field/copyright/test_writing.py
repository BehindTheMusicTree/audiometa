import pytest



from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestCopyrightWriting:
    def test_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            test_copyright = "© 2024 Test Label ID3v2"
            test_metadata = {UnifiedMetadataKey.COPYRIGHT: test_copyright}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            copyright_info = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info == test_copyright

    def test_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            test_copyright = "© 2024 Test Label RIFF"
            test_metadata = {UnifiedMetadataKey.COPYRIGHT: test_copyright}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.RIFF)
            copyright_info = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info == test_copyright

    def test_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            test_copyright = "© 2024 Test Label Vorbis"
            test_metadata = {UnifiedMetadataKey.COPYRIGHT: test_copyright}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.VORBIS)
            copyright_info = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COPYRIGHT)
            assert copyright_info == test_copyright

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with TempFileWithMetadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.COPYRIGHT: 123}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file.path, bad_metadata)
