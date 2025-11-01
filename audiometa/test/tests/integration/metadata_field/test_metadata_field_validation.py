import pytest
from pathlib import Path

from audiometa import get_unified_metadata_field, UnifiedMetadataKey, update_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError, MetadataFieldNotSupportedByLib, InvalidMetadataFieldTypeError
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestMetadataFieldValidation:
    """Test that get_unified_metadata_field raises MetadataFieldNotSupportedByMetadataFormatError 
    when a field is not supported by the specified format."""

    def test_replaygain_not_supported_by_riff(self, sample_wav_file: Path):
        with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError, match="UnifiedMetadataKey.REPLAYGAIN metadata not supported by this format"):
            get_unified_metadata_field(sample_wav_file, UnifiedMetadataKey.REPLAYGAIN, metadata_format=MetadataFormat.RIFF)

    def test_replaygain_not_supported_by_id3v1(self, sample_mp3_file: Path):
        with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError, match="UnifiedMetadataKey.REPLAYGAIN metadata not supported by this format"):
            get_unified_metadata_field(sample_mp3_file, UnifiedMetadataKey.REPLAYGAIN, metadata_format=MetadataFormat.ID3V1)

    def test_album_artists_not_supported_by_id3v1(self, sample_mp3_file: Path):
        with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError, match="UnifiedMetadataKey.ALBUM_ARTISTS metadata not supported by this format"):
            get_unified_metadata_field(sample_mp3_file, UnifiedMetadataKey.ALBUM_ARTISTS, metadata_format=MetadataFormat.ID3V1)

    def test_supported_field_works_with_riff(self, sample_wav_file: Path):
        title = get_unified_metadata_field(sample_wav_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.RIFF)
        assert title is None or isinstance(title, str)

    def test_supported_field_works_with_id3v1(self, sample_mp3_file: Path):
        title = get_unified_metadata_field(sample_mp3_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.ID3V1)
        assert title is None or isinstance(title, str)

    def test_unsupported_field_without_format_specification(self, sample_wav_file: Path):
        bpm = get_unified_metadata_field(sample_wav_file, UnifiedMetadataKey.BPM)
        assert bpm is None or isinstance(bpm, int)

    def test_rating_supported_by_riff_indirectly(self, sample_wav_file: Path):
        rating = get_unified_metadata_field(sample_wav_file, UnifiedMetadataKey.RATING, metadata_format=MetadataFormat.RIFF)
        assert rating is None or isinstance(rating, int)

    def test_field_not_supported_by_lib_exception_exists(self):
        with pytest.raises(MetadataFieldNotSupportedByLib, match="Test field not supported by library"):
            raise MetadataFieldNotSupportedByLib("Test field not supported by library")

    def test_field_not_supported_by_lib_concept(self, sample_wav_file: Path):
        with TempFileWithMetadata({}, "wav") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByLib, match="Test field not supported by library"):
                get_unified_metadata_field(test_file.path, 'Test field not supported by library')

    def test_invalid_metadata_field_type_error_wrong_type_for_list_field(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.ARTISTS: "should be list"}
                )
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.ARTISTS.value
            assert "list" in error.expected_type.lower()
            assert error.value == "should be list"

    def test_invalid_metadata_field_type_error_wrong_type_for_string_field(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(InvalidMetadataFieldTypeError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.TITLE: 12345}
                )
            error = exc_info.value
            assert error.field == UnifiedMetadataKey.TITLE.value
            assert error.value == 12345
