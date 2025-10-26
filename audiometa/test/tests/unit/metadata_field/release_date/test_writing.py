import pytest



from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestReleaseDateWriting:
    def test_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            test_release_date = "2024-01-01"
            test_metadata = {UnifiedMetadataKey.RELEASE_DATE: test_release_date}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V2)
            release_date = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE)
            assert release_date == test_release_date

    def test_riff(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            test_release_date = "2024-02-01"
            test_metadata = {UnifiedMetadataKey.RELEASE_DATE: test_release_date}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.RIFF)
            release_date = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE)
            assert release_date == test_release_date

    def test_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            test_release_date = "2024-03-01"
            test_metadata = {UnifiedMetadataKey.RELEASE_DATE: test_release_date}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.VORBIS)
            release_date = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE)
            assert release_date == test_release_date

    def test_id3v1(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            test_release_date = "2024"
            test_metadata = {UnifiedMetadataKey.RELEASE_DATE: test_release_date}
            update_metadata(test_file.path, test_metadata, metadata_format=MetadataFormat.ID3V1)
            release_date = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.RELEASE_DATE)
            assert release_date == test_release_date

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with TempFileWithMetadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.RELEASE_DATE: 20240101}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file.path, bad_metadata)
