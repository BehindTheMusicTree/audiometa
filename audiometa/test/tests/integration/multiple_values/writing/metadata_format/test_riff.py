import pytest

from audiometa import update_metadata
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestMultipleValuesRiff:
    def test_artists_concatenation(self):
        initial_metadata = {"title": "Test Song"}
        with temp_file_with_metadata(initial_metadata, "wav") as test_file:
            metadata = {UnifiedMetadataKey.ARTISTS: ["Artist 1", "Artist 2", "Artist 3"]}
            update_metadata(test_file, metadata, metadata_format=MetadataFormat.RIFF)

            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "TAG:artist=Artist 1//Artist 2//Artist 3" in raw_metadata

    def test_with_existing_artists_field(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_artists(test_file, ["Existing 1;Existing 2"])
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "TAG:artist=Existing 1;Existing 2" in raw_metadata

            metadata = {UnifiedMetadataKey.ARTISTS: ["Existing 1", "New 2"]}
            update_metadata(test_file, metadata, metadata_format=MetadataFormat.RIFF)

            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "TAG:artist=Existing 1//New 2" in raw_metadata
