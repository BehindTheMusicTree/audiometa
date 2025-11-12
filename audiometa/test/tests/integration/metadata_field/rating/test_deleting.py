import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestRatingDeleting:
    def test_delete_rating_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.RATING: 50},
                metadata_format=MetadataFormat.ID3V2,
                normalized_rating_max_value=100,
            )
            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) == 50
            )

            update_metadata(test_file, {UnifiedMetadataKey.RATING: None}, metadata_format=MetadataFormat.ID3V2)
            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
                is None
            )

    def test_delete_rating_id3v1(self):
        with (
            temp_file_with_metadata({}, "id3v1") as test_file,
            pytest.raises(MetadataFieldNotSupportedByMetadataFormatError),
        ):
            update_metadata(
                test_file,
                {UnifiedMetadataKey.RATING: 50},
                metadata_format=MetadataFormat.ID3V1,
                normalized_rating_max_value=100,
            )

    def test_delete_rating_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.RATING: 50},
                metadata_format=MetadataFormat.RIFF,
                normalized_rating_max_value=100,
            )
            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) == 50
            )

            update_metadata(test_file, {UnifiedMetadataKey.RATING: None}, metadata_format=MetadataFormat.RIFF)
            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
                is None
            )

    def test_delete_rating_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.RATING: 50},
                metadata_format=MetadataFormat.VORBIS,
                normalized_rating_max_value=100,
            )
            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) == 50
            )

            update_metadata(test_file, {UnifiedMetadataKey.RATING: None}, metadata_format=MetadataFormat.VORBIS)
            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
                is None
            )

    def test_delete_rating_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file,
                {
                    UnifiedMetadataKey.RATING: 70,
                    UnifiedMetadataKey.TITLE: "Test Title",
                    UnifiedMetadataKey.ARTISTS: ["Test Artist"],
                },
                normalized_rating_max_value=100,
            )

            update_metadata(test_file, {UnifiedMetadataKey.RATING: None})

            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
                is None
            )
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_rating_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.RATING: None})
            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
                is None
            )

    def test_delete_rating_zero(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.RATING: 0}, normalized_rating_max_value=100)
            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100) == 0
            )
            update_metadata(test_file, {UnifiedMetadataKey.RATING: None})
            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
                is None
            )
