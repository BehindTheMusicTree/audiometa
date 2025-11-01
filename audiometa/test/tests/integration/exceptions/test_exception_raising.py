import pytest

from audiometa import update_metadata
from audiometa.exceptions import (
    ConfigurationError,
    MetadataWritingConflictParametersError,
    InvalidRatingValueError,
    InvalidMetadataFieldTypeError,
)
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.MetadataWritingStrategy import MetadataWritingStrategy
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.integration
class TestExceptionRaising:

    def test_configuration_error_rating_without_max_value(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(ConfigurationError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.RATING: 75}
                )
            assert "normalized_rating_max_value" in str(exc_info.value).lower() or "max value" in str(exc_info.value).lower()

    def test_metadata_writing_conflict_parameters_error_both_strategy_and_format(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataWritingConflictParametersError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.TITLE: "Test"},
                    metadata_strategy=MetadataWritingStrategy.SYNC,
                    metadata_format=MetadataFormat.ID3V2
                )
            assert "metadata_strategy" in str(exc_info.value).lower()
            assert "metadata_format" in str(exc_info.value).lower()

    def test_invalid_rating_value_error_non_numeric_string(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(InvalidRatingValueError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.RATING: "invalid"},
                    normalized_rating_max_value=100
                )
            assert "invalid rating value" in str(exc_info.value).lower()

    def test_invalid_rating_value_error_non_numeric_type(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(InvalidRatingValueError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.RATING: {"not": "valid"}},
                    normalized_rating_max_value=100
                )
            assert "invalid rating value" in str(exc_info.value).lower()

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

    def test_configuration_error_id3v2_without_normalized_rating(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            with pytest.raises(ConfigurationError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.RATING: 75},
                    metadata_format=MetadataFormat.ID3V2
                )
            assert "normalized_rating_max_value" in str(exc_info.value).lower() or "max value" in str(exc_info.value).lower()

    def test_configuration_error_riff_without_normalized_rating(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            with pytest.raises(ConfigurationError) as exc_info:
                update_metadata(
                    test_file.path,
                    {UnifiedMetadataKey.RATING: 75},
                    metadata_format=MetadataFormat.RIFF
                )
            assert "normalized_rating_max_value" in str(exc_info.value).lower() or "max value" in str(exc_info.value).lower()

    def test_file_byte_mismatch_error_corrupted_flac(self, tmp_path):
        corrupted_flac = tmp_path / "corrupted.flac"
        corrupted_flac.write_bytes(b"fake file")
        from audiometa import AudioFile
        from audiometa.exceptions import FileByteMismatchError, FileCorruptedError
        
        audio_file = AudioFile(corrupted_flac)
        try:
            audio_file.get_duration_in_sec()
            pytest.fail("Should have raised FileByteMismatchError or FileCorruptedError")
        except (FileByteMismatchError, FileCorruptedError):
            pass

    def test_file_corrupted_error_invalid_wav(self, tmp_path):
        invalid_wav = tmp_path / "invalid.wav"
        invalid_wav.write_bytes(b"not a valid wav file")
        from audiometa import get_duration_in_sec
        from audiometa.exceptions import FileCorruptedError
        
        try:
            get_duration_in_sec(invalid_wav)
            pytest.fail("Should have raised FileCorruptedError")
        except (FileCorruptedError, RuntimeError):
            pass

