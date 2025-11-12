"""Custom exceptions for the audiometa library.

This module defines all custom exception classes used throughout the audiometa library for handling various error
conditions related to audio file metadata processing.
"""


class FileCorruptedError(Exception):
    """Raised when an audio file appears to be corrupted or invalid."""


class FlacMd5CheckFailedError(FileCorruptedError):
    """Raised when FLAC MD5 checksum verification fails."""


class FileByteMismatchError(FileCorruptedError):
    """Raised when file bytes do not match expected content."""


class InvalidChunkDecodeError(FileCorruptedError):
    """Raised when a chunk cannot be decoded properly."""


class DurationNotFoundError(FileCorruptedError):
    """Raised when audio duration cannot be determined."""


class AudioFileMetadataParseError(FileCorruptedError):
    """Raised when audio file metadata cannot be parsed from external tools.

    This error indicates that the output from tools like ffprobe could not be
    parsed as valid JSON or metadata format.

    Examples:
        - ffprobe returns invalid JSON when probing audio files
        - Metadata parsing fails due to unexpected output format
    """


class FileTypeNotSupportedError(Exception):
    """Raised when the audio file type is not supported by the library."""


class ConfigurationError(Exception):
    """Raised when there is a configuration error in the metadata manager.

    This error indicates that the metadata manager was not properly configured or initialized with the required
    parameters.
    """


class MetadataFormatNotSupportedByAudioFormatError(Exception):
    """Raised when attempting to read metadata from a format not supported by the audio format of the file.

    This error indicates that the requested metadata format is not supported by the audio format of the file.

    Examples:
        - Trying to read metadata from RIFF format from an MP3 file
        - Trying to read metadata from Vorbis format from a WAV file
    """


class MetadataFieldNotSupportedByMetadataFormatError(Exception):
    """Raised when attempting to read or write metadata not supported by the format.

    This error indicates a format limitation (e.g., trying to write BPM to RIFF),
    not a code error. The format simply does not support the requested metadata field.

    Examples:
        - Trying to read/write ratings to RIFF
        - Trying to read/write BPM to ID3v1
        - Trying to read/write album artist to ID3v1
    """


class MetadataFieldNotSupportedByLibError(Exception):
    """Raised when attempting to read or write a metadata field that is not supported by the library at all.

    This error indicates that the requested metadata field is not implemented or supported
    by any format in the library, regardless of the audio file format.

    Examples:
        - Trying to read/write a custom field that doesn't exist in UnifiedMetadataKey
        - Trying to read/write a field that is not implemented in any metadata manager
    """


class MetadataWritingConflictParametersError(Exception):
    """Raised when conflicting metadata writing parameters are specified.

    This error indicates that the user has provided parameters that cannot
    be used together for metadata writing operations.

    Examples:
        - Specifying both metadata_strategy and metadata_format
        - Other mutually exclusive metadata writing parameters
    """


class InvalidMetadataFieldTypeError(TypeError):
    """Raised when a metadata field value has an unexpected type.

    Attributes:
        field: str - the unified metadata field name (e.g. 'artists')
        expected_type: str - human-readable expected type (e.g. 'list[str]')
        actual_type: str - name of the actual type received
        value: object - the actual value passed
    """

    def __init__(self, field: str, expected_type: str, actual_value: object):
        """Initialize the exception with field details.

        Args:
            field: The unified metadata field name.
            expected_type: Human-readable expected type.
            actual_value: The actual value that was passed.
        """
        actual_type = type(actual_value).__name__
        message = (
            f"Invalid type for metadata field '{field}': expected {expected_type}, "
            f"got {actual_type} (value={actual_value!r})"
        )
        super().__init__(message)
        self.field = field
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.value = actual_value


class InvalidRatingValueError(Exception):
    """Raised when an invalid rating value is provided.

    This error indicates that the rating value cannot be converted to a valid
    numeric rating or is not in the expected format.

    Examples:
        - Non-numeric string values like "invalid" or "abc"
        - Values that cannot be converted to integers
        - None values when a rating is expected
    """


class InvalidMetadataFieldFormatError(ValueError):
    """Raised when a metadata field value has an invalid format.

    This error indicates that the value has the correct type but does not
    match the required format pattern.

    Attributes:
        field: str - the unified metadata field name (e.g. 'release_date')
        expected_format: str - human-readable expected format (e.g. 'YYYY or YYYY-MM-DD')
        value: object - the actual value passed
    """

    def __init__(self, field: str, expected_format: str, actual_value: object):
        """Initialize the exception with field format details.

        Args:
            field: The unified metadata field name.
            expected_format: Human-readable expected format.
            actual_value: The actual value that was passed.
        """
        message = f"Invalid format for metadata field '{field}': expected {expected_format}, got {actual_value!r}"
        super().__init__(message)
        self.field = field
        self.expected_format = expected_format
        self.value = actual_value
