import pytest

from audiometa import update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestMultipleValuesVorbis:
    def test_write_multiple_artists(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            # Write multiple artists using update_metadata
            metadata = {UnifiedMetadataKey.ARTISTS: ["Artist One", "Artist Two", "Artist Three"]}

            update_metadata(test_file, metadata, metadata_format=MetadataFormat.VORBIS)
            VorbisMetadataSetter.add_title(test_file, "Test Song")
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "ARTIST=Artist One" in raw_metadata
            assert "ARTIST=Artist Two" in raw_metadata
            assert "ARTIST=Artist Three" in raw_metadata

    def test_with_existing_artists_fields(self):
        # Start with an existing artist field
        with temp_file_with_metadata({}, "flac") as test_file:
            # create an existing value using setter
            VorbisMetadataSetter.set_artists(test_file, ["Existing 1; Existing 2"])
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "Existing 1; Existing 2" in raw_metadata

            metadata = {UnifiedMetadataKey.ARTISTS: ["Existing 1", "New 2"]}
            update_metadata(test_file, metadata, metadata_format=MetadataFormat.VORBIS)

            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "Existing 1" in raw_metadata
            assert "New 2" in raw_metadata
            assert "Existing 2" not in raw_metadata

    def test_with_existing_artists_fields_with_lower_case_key(self):
        # Start with an existing artist field in lower case
        with temp_file_with_metadata({}, "flac") as test_file:
            # create an existing value using setter
            VorbisMetadataSetter.set_artists(test_file, ["ExistingLower 1; ExistingLower 2"], key_lower_case=True)
            raw_output = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "artist=ExistingLower 1; ExistingLower 2" in raw_output

            metadata = {UnifiedMetadataKey.ARTISTS: ["ExistingLower 1", "New 2"]}
            update_metadata(test_file, metadata, metadata_format=MetadataFormat.VORBIS)

            raw_output = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "ARTIST=ExistingLower 1" in raw_output
            assert "ARTIST=New 2" in raw_output
