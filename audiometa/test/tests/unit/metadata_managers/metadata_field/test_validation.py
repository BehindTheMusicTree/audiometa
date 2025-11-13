import pytest

from audiometa import validate_metadata_for_update
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestValidateMetadata:
    """Test the integrate validate_metadata_for_update function.

    This class tests the high-level validation function that integrates multiple validation layers. Specific field
    validation (type, format) is tested separately in metadata_field/ test files.
    """

    def test_empty_dict_raises_error(self):
        with pytest.raises(ValueError, match="no metadata fields specified"):
            validate_metadata_for_update({})

    def test_none_values_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.TITLE: None})

        validate_metadata_for_update(
            {
                UnifiedMetadataKey.TITLE: None,
                UnifiedMetadataKey.ARTISTS: None,
                UnifiedMetadataKey.ALBUM: None,
            }
        )

    def test_empty_string_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.TITLE: ""})

    def test_empty_list_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.ARTISTS: []})

    def test_list_with_none_values_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.ARTISTS: [None, None]})
        validate_metadata_for_update({UnifiedMetadataKey.ARTISTS: [None]})
        validate_metadata_for_update({UnifiedMetadataKey.GENRES_NAMES: [None, None, None]})

    def test_empty_string_and_empty_list_allowed(self):
        validate_metadata_for_update({UnifiedMetadataKey.TITLE: "", UnifiedMetadataKey.ARTISTS: []})

    def test_valid_metadata_passes(self):
        validate_metadata_for_update({UnifiedMetadataKey.TITLE: "Song Title"})
        validate_metadata_for_update({UnifiedMetadataKey.ARTISTS: ["Artist 1", "Artist 2"]})
        validate_metadata_for_update({UnifiedMetadataKey.ALBUM: "Album Name"})

    def test_multiple_valid_fields_passes(self):
        validate_metadata_for_update(
            {
                UnifiedMetadataKey.TITLE: "Song Title",
                UnifiedMetadataKey.ARTISTS: ["Artist"],
                UnifiedMetadataKey.ALBUM: "Album",
            }
        )

    def test_mixed_none_and_valid_fields_passes(self):
        validate_metadata_for_update(
            {
                UnifiedMetadataKey.TITLE: None,
                UnifiedMetadataKey.ARTISTS: ["Artist"],
            }
        )

    def test_combined_validation_rating_and_release_date(self):
        validate_metadata_for_update(
            {
                UnifiedMetadataKey.RATING: 50,
                UnifiedMetadataKey.RELEASE_DATE: "2024-01-01",
            },
            normalized_rating_max_value=100,
        )

    def test_combined_validation_with_empty_fields(self):
        validate_metadata_for_update(
            {
                UnifiedMetadataKey.TITLE: "",
                UnifiedMetadataKey.ARTISTS: [],
                UnifiedMetadataKey.RATING: 50,
            },
            normalized_rating_max_value=100,
        )
