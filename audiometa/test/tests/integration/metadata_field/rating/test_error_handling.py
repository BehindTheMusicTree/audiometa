import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.exceptions import FileTypeNotSupportedError, InvalidMetadataFieldTypeError, InvalidRatingValueError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestRatingErrorHandling:
    def test_rating_unsupported_file_type(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            temp_file_path.write_bytes(b"fake audio content")
            temp_txt = temp_file_path.with_suffix(".txt")
            temp_txt.write_bytes(b"fake audio content")

            with pytest.raises(FileTypeNotSupportedError):
                get_unified_metadata_field(str(temp_txt), UnifiedMetadataKey.RATING)

            with pytest.raises(FileTypeNotSupportedError):
                update_metadata(str(temp_txt), {UnifiedMetadataKey.RATING: 85})

    def test_rating_nonexistent_file(self):
        nonexistent_file = "nonexistent_file.mp3"

        with pytest.raises(FileNotFoundError):
            get_unified_metadata_field(nonexistent_file, UnifiedMetadataKey.RATING)

        with pytest.raises(FileNotFoundError):
            update_metadata(nonexistent_file, {UnifiedMetadataKey.RATING: 85})

    def test_write_fractional_values(self):
        # Fractional values are now supported for half-star ratings (consistent with classic star rating systems)
        basic_metadata = {"title": "Test Title", "artist": "Test Artist"}
        with temp_file_with_metadata(basic_metadata, "mp3") as test_file:
            # 25.5/100 maps to index 3 (1.5 stars), which is valid
            update_metadata(
                test_file,
                {UnifiedMetadataKey.RATING: 25.5},
                normalized_rating_max_value=100,
                metadata_format=MetadataFormat.ID3V2,
            )
            # Verify it was written correctly
            rating = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert rating == 30  # 1.5 stars = 30 on 100-scale

    def test_rating_invalid_string_value(self):
        with (
            temp_file_with_metadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file,
            pytest.raises(
                InvalidMetadataFieldTypeError,
                match="Invalid type for metadata field 'rating': expected Union\\[int, float\\], got str",
            ),
        ):
            update_metadata(test_file, {UnifiedMetadataKey.RATING: "invalid"}, normalized_rating_max_value=100)

    def test_rating_negative_value_rejected_in_normalized_mode(self):
        with (
            temp_file_with_metadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file,
            pytest.raises(InvalidRatingValueError) as exc_info,
        ):
            update_metadata(test_file, {UnifiedMetadataKey.RATING: -1}, normalized_rating_max_value=100)
        assert "must be non-negative" in str(exc_info.value)

    def test_rating_over_max_value_rejected_in_normalized_mode(self):
        with temp_file_with_metadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            with pytest.raises(InvalidRatingValueError) as exc_info:
                update_metadata(test_file, {UnifiedMetadataKey.RATING: 101}, normalized_rating_max_value=100)
            assert "out of range" in str(exc_info.value)
            assert "must be between 0 and 100" in str(exc_info.value)

    def test_rating_none_value(self):
        with temp_file_with_metadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.RATING: None}, normalized_rating_max_value=100)
            metadata = get_unified_metadata_field(test_file, UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
            assert metadata is None

    def test_rating_without_max_value_allows_any_non_negative_integer(self):
        with temp_file_with_metadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            # Any non-negative integer value should be allowed when normalized_rating_max_value is None
            update_metadata(test_file, {UnifiedMetadataKey.RATING: 128}, metadata_format=MetadataFormat.ID3V2)
            update_metadata(test_file, {UnifiedMetadataKey.RATING: 75}, metadata_format=MetadataFormat.ID3V2)
            update_metadata(test_file, {UnifiedMetadataKey.RATING: 0}, metadata_format=MetadataFormat.ID3V2)

            # Negative values should be rejected
            with pytest.raises(InvalidRatingValueError) as exc_info:
                update_metadata(test_file, {UnifiedMetadataKey.RATING: -1}, metadata_format=MetadataFormat.ID3V2)
            assert "must be non-negative" in str(exc_info.value)

            # Valid value in BASE_100_PROPORTIONAL profile (Vorbis uses this)
            with temp_file_with_metadata(
                {"title": "Test Title", "artist": "Test Artist"}, "flac"
            ) as test_file_flac_path:
                update_metadata(
                    test_file_flac_path, {UnifiedMetadataKey.RATING: 50}, metadata_format=MetadataFormat.VORBIS
                )
                update_metadata(
                    test_file_flac_path, {UnifiedMetadataKey.RATING: 128}, metadata_format=MetadataFormat.VORBIS
                )

    def test_rating_with_normalized_max_validates_profile_values(self):
        with temp_file_with_metadata({"title": "Test Title", "artist": "Test Artist"}, "mp3") as test_file:
            # Valid: 50/100 maps to star rating index 5 (2.5 stars), which is valid
            update_metadata(
                test_file,
                {UnifiedMetadataKey.RATING: 50},
                normalized_rating_max_value=100,
                metadata_format=MetadataFormat.ID3V2,
            )

            # Invalid: 37/100 maps to star rating index 4 (2 stars), which is valid
            # But 110/100 would map to index 11, which is > 10 (invalid)
            with pytest.raises(InvalidRatingValueError) as exc_info:
                update_metadata(
                    test_file,
                    {UnifiedMetadataKey.RATING: 110},
                    normalized_rating_max_value=100,
                    metadata_format=MetadataFormat.ID3V2,
                )
            assert "out of range" in str(exc_info.value) or "do not exist in any supported writing profile" in str(
                exc_info.value
            )

    def test_invalid_rating_value_error_non_numeric_string(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                update_metadata(test_file, {UnifiedMetadataKey.RATING: "invalid"}, normalized_rating_max_value=100)
            assert "invalid type for metadata field 'rating'" in str(exc_info.value).lower()

    def test_invalid_rating_value_error_non_numeric_type(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                update_metadata(
                    test_file, {UnifiedMetadataKey.RATING: {"not": "valid"}}, normalized_rating_max_value=100
                )
            assert "invalid type for metadata field 'rating'" in str(exc_info.value).lower()
