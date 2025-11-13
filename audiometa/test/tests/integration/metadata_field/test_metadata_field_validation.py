from pathlib import Path

import pytest

from audiometa import UnifiedMetadataKey, get_unified_metadata_field, update_metadata
from audiometa.exceptions import (
    InvalidMetadataFieldTypeError,
    MetadataFieldNotSupportedByLibError,
    MetadataFieldNotSupportedByMetadataFormatError,
)
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat


@pytest.mark.integration
class TestMetadataFieldValidation:
    """Test that get_unified_metadata_field raises MetadataFieldNotSupportedByMetadataFormatError when a field is not
    supported by the specified format."""

    def test_replaygain_not_supported_by_riff(self, sample_wav_file: Path):
        with pytest.raises(
            MetadataFieldNotSupportedByMetadataFormatError,
            match="UnifiedMetadataKey.REPLAYGAIN metadata not supported by RIFF format",
        ):
            get_unified_metadata_field(
                sample_wav_file, UnifiedMetadataKey.REPLAYGAIN, metadata_format=MetadataFormat.RIFF
            )

    def test_replaygain_not_supported_by_id3v1(self, sample_mp3_file: Path):
        with pytest.raises(
            MetadataFieldNotSupportedByMetadataFormatError,
            match="UnifiedMetadataKey.REPLAYGAIN metadata not supported by ID3v1 format",
        ):
            get_unified_metadata_field(
                sample_mp3_file, UnifiedMetadataKey.REPLAYGAIN, metadata_format=MetadataFormat.ID3V1
            )

    def test_album_artists_not_supported_by_id3v1(self, sample_mp3_file: Path):
        with pytest.raises(
            MetadataFieldNotSupportedByMetadataFormatError,
            match="UnifiedMetadataKey.ALBUM_ARTISTS metadata not supported by ID3v1 format",
        ):
            get_unified_metadata_field(
                sample_mp3_file, UnifiedMetadataKey.ALBUM_ARTISTS, metadata_format=MetadataFormat.ID3V1
            )

    def test_supported_field_works_with_riff(self, sample_wav_file: Path):
        title = get_unified_metadata_field(
            sample_wav_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.RIFF
        )
        assert title is None or isinstance(title, str)

    def test_supported_field_works_with_id3v1(self, sample_mp3_file: Path):
        title = get_unified_metadata_field(
            sample_mp3_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.ID3V1
        )
        assert title is None or isinstance(title, str)

    def test_unsupported_field_without_format_specification(self, sample_wav_file: Path):
        bpm = get_unified_metadata_field(sample_wav_file, UnifiedMetadataKey.BPM)
        assert bpm is None or isinstance(bpm, int)

    def test_rating_supported_by_riff_indirectly(self, sample_wav_file: Path):
        rating = get_unified_metadata_field(
            sample_wav_file, UnifiedMetadataKey.RATING, metadata_format=MetadataFormat.RIFF
        )
        assert rating is None or isinstance(rating, int)

    def test_field_not_supported_by_lib_exception_exists(self):
        msg = "Test field not supported by library"
        with pytest.raises(MetadataFieldNotSupportedByLibError, match="Test field not supported by library"):
            raise MetadataFieldNotSupportedByLibError(msg)

    def test_field_not_supported_by_lib_concept(self):
        with (
            temp_file_with_metadata({}, "wav") as test_file,
            pytest.raises(MetadataFieldNotSupportedByLibError, match="Test field not supported by library"),
        ):
            get_unified_metadata_field(test_file, "Test field not supported by library")

    def test_valid_string_key_works(self, sample_mp3_file: Path):
        """Test that passing a string matching a UnifiedMetadataKey enum value works."""
        # Test various string values that match enum values
        title = get_unified_metadata_field(sample_mp3_file, "title")
        assert title is None or isinstance(title, str)

        artists = get_unified_metadata_field(sample_mp3_file, "artists")
        assert artists is None or isinstance(artists, list)

        rating = get_unified_metadata_field(sample_mp3_file, "rating")
        assert rating is None or isinstance(rating, int)

        # Verify it works the same as enum
        title_enum = get_unified_metadata_field(sample_mp3_file, UnifiedMetadataKey.TITLE)
        assert title == title_enum

    def test_invalid_string_key_raises_error(self, sample_mp3_file: Path):
        """Test that passing an invalid string raises MetadataFieldNotSupportedByLibError."""
        with pytest.raises(
            MetadataFieldNotSupportedByLibError, match="invalid_field metadata not supported by the library"
        ):
            get_unified_metadata_field(sample_mp3_file, "invalid_field")

    def test_all_valid_enum_values_work(self, sample_mp3_file: Path):
        """Test that all valid UnifiedMetadataKey enum values are accepted (not rejected as invalid enum values)."""
        for key in UnifiedMetadataKey:
            # Should not raise MetadataFieldNotSupportedByLibError for invalid enum value
            # (it's okay if it raises for "not supported by any format" - that's different)
            try:
                result = get_unified_metadata_field(sample_mp3_file, key)
                # Result can be None if field is not present, which is valid
                assert result is None or isinstance(result, str | int | float | list)
            except MetadataFieldNotSupportedByLibError as e:
                # Only fail if the error message indicates invalid enum value
                # It's okay if it raises for "not supported by any format" - that's different
                if "not supported by any format" not in str(e):
                    raise

    def test_invalid_metadata_field_type_error_wrong_type_for_list_field(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                update_metadata(test_file, {UnifiedMetadataKey.ARTISTS: "should be list"})
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.ARTISTS.value
            assert "list" in error.expected_type.lower()
            assert error.value == "should be list"

    def test_invalid_metadata_field_type_error_wrong_type_for_string_field(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                update_metadata(test_file, {UnifiedMetadataKey.TITLE: 12345})
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.TITLE.value
            assert error.value == 12345
