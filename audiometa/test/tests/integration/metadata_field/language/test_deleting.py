import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestLanguageDeleting:
    def test_delete_language_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_language(test_file, "en")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE) == "en"

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.LANGUAGE: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE) is None

    def test_delete_language_id3v1(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError

        with (
            temp_file_with_metadata({}, "id3v1") as test_file,
            pytest.raises(MetadataFieldNotSupportedByMetadataFormatError),
        ):
            # Deleting should fail since the field isn't supported
            update_metadata(test_file, {UnifiedMetadataKey.LANGUAGE: None}, metadata_format=MetadataFormat.ID3V1)

    def test_delete_language_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_language(test_file, "en")
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "TAG:language=en" in raw_metadata

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.LANGUAGE: None}, metadata_format=MetadataFormat.RIFF)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE) is None

    def test_delete_language_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_language(test_file, "en")
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE) == "en"

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.LANGUAGE: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE) is None

    def test_delete_language_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_language(test_file, "en")
            ID3v2MetadataSetter.set_title(test_file, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file, "Test Artist")

            # Delete only language using library API
            update_metadata(test_file, {UnifiedMetadataKey.LANGUAGE: None}, metadata_format=MetadataFormat.ID3V2)

            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_language_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            # Try to delete language that doesn't exist
            update_metadata(test_file, {UnifiedMetadataKey.LANGUAGE: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE) is None

    def test_delete_language_empty_string(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.LANGUAGE: ""}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.LANGUAGE) is None
