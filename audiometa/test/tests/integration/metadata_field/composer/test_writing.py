import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestComposerWriting:
    def test_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_composer = "Test Composer ID3v2"
            test_metadata = {UnifiedMetadataKey.COMPOSERS: [test_composer]}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2)
            composer = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMPOSERS)
            assert composer == [test_composer]

    def test_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            test_composer = "Test Composer RIFF"
            test_metadata = {UnifiedMetadataKey.COMPOSERS: [test_composer]}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.RIFF)
            composer = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMPOSERS)
            assert composer == [test_composer]

    def test_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            test_composer = "Test Composer Vorbis"
            test_metadata = {UnifiedMetadataKey.COMPOSERS: [test_composer]}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.VORBIS)
            composer = get_unified_metadata_field(test_file, UnifiedMetadataKey.COMPOSERS)
            assert composer == [test_composer]

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with temp_file_with_metadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.COMPOSERS: 12345}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file, bad_metadata)
