# Error Handling Guide: Exceptions and Error Management

This document provides comprehensive documentation for all exceptions that can be raised by the audiometa library, organized by category with detailed explanations, common causes, and usage examples.

**Note**: For metadata field support and handling, see the **[Metadata Field Guide](METADATA_FIELD_GUIDE.md)**. For audio technical information, see the **[Audio Technical Info Guide](AUDIO_TECHNICAL_INFO_GUIDE.md)**.

## Table of Contents

- [All Library Exceptions](#all-library-exceptions)
- [File-Related Exceptions](#file-related-exceptions)
- [Metadata Format Exceptions](#metadata-format-exceptions)
- [Validation Exceptions](#validation-exceptions)
- [Configuration Exceptions](#configuration-exceptions)
- [Standard Python Exceptions](#standard-python-exceptions)
- [Exception Handling for Mutagen Operations](#exception-handling-for-mutagen-operations)

## All Library Exceptions

The library defines the following custom exceptions, all available from `audiometa.exceptions`:

```python
from audiometa.exceptions import (
    # File-related exceptions
    FileCorruptedError,
    FlacMd5CheckFailedError,
    FileByteMismatchError,
    InvalidChunkDecodeError,
    DurationNotFoundError,
    AudioFileMetadataParseError,
    FileTypeNotSupportedError,

    # Metadata format exceptions
    MetadataFormatNotSupportedByAudioFormatError,
    MetadataFieldNotSupportedByMetadataFormatError,
    MetadataFieldNotSupportedByLibError,
    MetadataWritingConflictParametersError,

    # Validation exceptions
    InvalidMetadataFieldTypeError,
    InvalidMetadataFieldFormatError,
    InvalidRatingValueError,

    # Configuration exceptions
    ConfigurationError,
)
```

## File-Related Exceptions

### `FileCorruptedError`

**Base exception for file corruption errors.** All file corruption-related exceptions inherit from this.

**When raised:**

- File content doesn't match the expected format (e.g., invalid MP3/FLAC/WAV structure)
- Mutagen operations fail due to corrupted file data
- File validation fails during initialization
- Reading duration or technical info fails due to corruption

**Common causes:**

- Truncated or corrupted audio files
- Files with invalid headers or structure
- Files that have been partially overwritten
- Mutagen-specific parsing errors

**Example:**

```python
from audiometa import get_unified_metadata
from audiometa.exceptions import FileCorruptedError

try:
    metadata = get_unified_metadata("corrupted.mp3")
except FileCorruptedError as e:
    print(f"File is corrupted: {e}")
    # Access original exception if available
    if e.__cause__:
        print(f"Original error: {e.__cause__}")
```

### `FlacMd5CheckFailedError` (subclass of `FileCorruptedError`)

**Raised when FLAC MD5 checksum verification fails.**

**When raised:**

- FLAC file's MD5 checksum doesn't match the audio data
- MD5 checksum verification detects file corruption
- `is_flac_md5_valid()` detects invalid checksum

**Example:**

```python
from audiometa import is_flac_md5_valid
from audiometa.exceptions import FlacMd5CheckFailedError

try:
    is_valid = is_flac_md5_valid("corrupted.flac")
except FlacMd5CheckFailedError:
    print("FLAC file MD5 checksum is invalid - file may be corrupted")
```

### `FileByteMismatchError` (subclass of `FileCorruptedError`)

**Raised when file bytes do not match expected content.**

**When raised:**

- FLAC file header indicates a different file size than actual bytes read
- File size mismatch detected during parsing

**Example:**

```python
from audiometa import get_duration_in_sec
from audiometa.exceptions import FileByteMismatchError

try:
    duration = get_duration_in_sec("mismatched.flac")
except FileByteMismatchError as e:
    print(f"File size mismatch: {e}")
```

### `InvalidChunkDecodeError` (subclass of `FileCorruptedError`)

**Raised when a chunk cannot be decoded properly.**

**When raised:**

- FLAC chunk decoding fails
- Invalid chunk structure detected in audio file

**Example:**

```python
from audiometa import get_duration_in_sec
from audiometa.exceptions import InvalidChunkDecodeError

try:
    duration = get_duration_in_sec("invalid_chunks.flac")
except InvalidChunkDecodeError as e:
    print(f"Failed to decode chunks: {e}")
```

### `DurationNotFoundError` (subclass of `FileCorruptedError`)

**Raised when audio duration cannot be determined.**

**When raised:**

- Duration cannot be read from MP3/FLAC/WAV file
- All fallback methods for reading duration fail
- Duration is zero or invalid

**Example:**

```python
from audiometa import get_duration_in_sec
from audiometa.exceptions import DurationNotFoundError

try:
    duration = get_duration_in_sec("invalid.mp3")
except DurationNotFoundError as e:
    print(f"Could not determine duration: {e}")
```

### `AudioFileMetadataParseError` (subclass of `FileCorruptedError`)

**Raised when audio file metadata cannot be parsed from external tools.**

**When raised:**

- `ffprobe` returns invalid JSON when probing audio files
- Metadata parsing fails due to unexpected output format
- External tool output cannot be parsed

**Example:**

```python
from audiometa import get_duration_in_sec
from audiometa.exceptions import AudioFileMetadataParseError

try:
    duration = get_duration_in_sec("file.wav")
except AudioFileMetadataParseError as e:
    print(f"Failed to parse metadata: {e}")
```

### `FileTypeNotSupportedError`

**Raised when the audio file type is not supported by the library.**

**When raised:**

- File extension is not supported (e.g., `.ogg`, `.txt`)
- File type is not in the list of supported formats
- Unsupported file type passed to library functions (e.g., `get_unified_metadata()`, `update_metadata()`)

**Supported formats:** `.mp3`, `.flac`, `.wav`

**Example:**

```python
from audiometa import get_unified_metadata
from audiometa.exceptions import FileTypeNotSupportedError

try:
    metadata = get_unified_metadata("song.ogg")
except FileTypeNotSupportedError as e:
    print(f"File type not supported: {e}")
```

## Metadata Format Exceptions

### `MetadataFormatNotSupportedByAudioFormatError`

**Raised when attempting to read metadata from a format not supported by the audio format of the file.**

**When raised:**

- Trying to read RIFF metadata from an MP3 file
- Trying to read Vorbis metadata from a WAV file
- Requesting a metadata format incompatible with the audio file type

**Example:**

```python
from audiometa import delete_all_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.exceptions import MetadataFormatNotSupportedByAudioFormatError

try:
    delete_all_metadata("song.mp3", metadata_format=MetadataFormat.RIFF)
except MetadataFormatNotSupportedByAudioFormatError as e:
    print(f"Format not supported for this audio type: {e}")
```

### `MetadataFieldNotSupportedByMetadataFormatError`

**Raised when attempting to read or write metadata not supported by the format.**

**When raised:**

- Trying to write BPM to RIFF format
- Trying to write rating to ID3v1 format
- Trying to write album artist to ID3v1 format
- Field is not supported by the requested metadata format (format limitation, not code error)

**Example:**

```python
from audiometa import update_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError

try:
    update_metadata("song.wav", {"bpm": 120}, metadata_format=MetadataFormat.RIFF)
except MetadataFieldNotSupportedByMetadataFormatError as e:
    print(f"Field not supported by format: {e}")
```

### `MetadataFieldNotSupportedByLibError`

**Raised when attempting to read or write a metadata field that is not supported by the library at all.**

**When raised:**

- Trying to read/write a custom field that doesn't exist in `UnifiedMetadataKey`
- Field is not implemented in any metadata manager
- Field is not supported by any format in the library

**Example:**

```python
from audiometa import update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByLibError

try:
    update_metadata("song.mp3", {"custom_field": "value"})
except MetadataFieldNotSupportedByLibError as e:
    print(f"Field not supported by library: {e}")
```

### `MetadataWritingConflictParametersError`

**Raised when conflicting metadata writing parameters are specified.**

**When raised:**

- Specifying both `metadata_strategy` and `metadata_format` parameters
- Mutually exclusive parameters are provided together

**Example:**

```python
from audiometa import update_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.MetadataWritingStrategy import MetadataWritingStrategy
from audiometa.exceptions import MetadataWritingConflictParametersError

try:
    update_metadata("song.mp3", {"title": "Song"},
                    metadata_format=MetadataFormat.ID3V2,
                    metadata_strategy=MetadataWritingStrategy.SYNC)
except MetadataWritingConflictParametersError as e:
    print(f"Conflicting parameters: {e}")
```

## Validation Exceptions

### `InvalidMetadataFieldTypeError` (subclass of `TypeError`)

**Raised when a metadata field value has an unexpected type.**

**When raised:**

- Providing a string when a list is expected (e.g., `artists` field)
- Providing a list when a string is expected (e.g., `title` field)
- Type mismatch during metadata validation

**Attributes:**

- `field`: The unified metadata field name
- `expected_type`: Human-readable expected type
- `actual_type`: Name of the actual type received
- `value`: The actual value passed

**Example:**

```python
from audiometa import validate_metadata_for_update, UnifiedMetadataKey
from audiometa.exceptions import InvalidMetadataFieldTypeError

try:
    validate_metadata_for_update({UnifiedMetadataKey.ARTISTS: "Artist Name"})
except InvalidMetadataFieldTypeError as e:
    print(f"Invalid type: {e}")
    print(f"Field: {e.field}")
    print(f"Expected: {e.expected_type}, Got: {e.actual_type}")
```

### `InvalidMetadataFieldFormatError` (subclass of `ValueError`)

**Raised when a metadata field value has an invalid format.**

**When raised:**

- Invalid release date format (e.g., `"2024/01/01"` instead of `"2024-01-01"`)
- Format validation fails for date fields
- Value has correct type but wrong format pattern

**Attributes:**

- `field`: The unified metadata field name
- `expected_format`: Human-readable expected format
- `value`: The actual value passed

**Example:**

```python
from audiometa import validate_metadata_for_update, UnifiedMetadataKey
from audiometa.exceptions import InvalidMetadataFieldFormatError

try:
    validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: "2024/01/01"})
except InvalidMetadataFieldFormatError as e:
    print(f"Invalid format: {e}")
    print(f"Field: {e.field}")
    print(f"Expected: {e.expected_format}, Got: {e.value}")
```

### `InvalidRatingValueError`

**Raised when an invalid rating value is provided.**

**When raised:**

- Non-numeric string values like `"invalid"` or `"abc"`
- Values that cannot be converted to integers
- `None` values when a rating is expected
- Negative rating values
- Rating values exceeding the maximum allowed value

**Example:**

```python
from audiometa import validate_metadata_for_update, UnifiedMetadataKey
from audiometa.exceptions import InvalidRatingValueError

try:
    validate_metadata_for_update({UnifiedMetadataKey.RATING: "invalid"})
except InvalidRatingValueError as e:
    print(f"Invalid rating value: {e}")

try:
    validate_metadata_for_update({UnifiedMetadataKey.RATING: -1})
except InvalidRatingValueError as e:
    print(f"Invalid rating value: {e}")
```

## Configuration Exceptions

### `ConfigurationError`

**Raised when there is a configuration error in the metadata manager.**

**When raised:**

- Metadata manager was not properly configured
- Required initialization parameters are missing
- Configuration is invalid or incomplete

**Example:**

```python
from audiometa.exceptions import ConfigurationError

try:
    # Some operation that requires proper configuration
    pass
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Standard Python Exceptions

The library may also raise standard Python exceptions:

### `FileNotFoundError`

**Raised when a file does not exist.**

**When raised:**

- File path provided doesn't exist
- File was deleted or moved before operation

**Example:**

```python
from audiometa import get_unified_metadata

try:
    metadata = get_unified_metadata("nonexistent.mp3")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

### `IOError`, `OSError`, `PermissionError`

**Raised for system-level I/O errors.**

**When raised:**

- File permission issues
- Disk I/O errors
- System-level file access problems
- These are re-raised as-is from mutagen operations (not converted to `FileCorruptedError`)

**Example:**

```python
from audiometa import update_metadata

try:
    update_metadata("/readonly/file.mp3", {"title": "Song"})
except PermissionError as e:
    print(f"Permission denied: {e}")
except OSError as e:
    print(f"OS error: {e}")
```

## Exception Handling for Mutagen Operations

The library uses mutagen internally for reading and writing metadata. All mutagen operations are wrapped with proper exception handling to ensure that mutagen-specific exceptions are converted to library exceptions (`FileCorruptedError`) with descriptive error messages.

**Standard I/O exceptions** (`IOError`, `OSError`, `PermissionError`) are re-raised as-is, as they indicate system-level issues that should be handled by the caller.

**Mutagen-specific exceptions** and other unexpected exceptions are converted to `FileCorruptedError` with descriptive messages indicating the operation that failed.

**Operations with mutagen exception handling:**

- **Metadata reading and writing**: All `mutagen.save()` operations
- **FLAC duration reading**: Reading duration from FLAC files using `mutagen.flac.FLAC()`
- **FLAC MD5 fixing**: Operations that may encounter mutagen exceptions during MD5 checksum repair
- **RIFF metadata extraction**: `mutagen.wave.WAVE()` object creation
- **ID3v2 save operations**: All ID3v2 metadata save operations

**Example:**

```python
from audiometa import get_duration_in_sec, fix_md5_checking
from audiometa.exceptions import FileCorruptedError

try:
    duration = get_duration_in_sec("song.flac")
except FileCorruptedError as e:
    print(f"Failed to read FLAC file: {e}")
    # The original mutagen exception is preserved via exception chaining
    print(f"Original error: {e.__cause__}")

try:
    fixed_file = fix_md5_checking("corrupted.flac")
except FileCorruptedError as e:
    print(f"Failed to fix MD5 checksum: {e}")
except (OSError, PermissionError) as e:
    print(f"System error: {e}")
```

**Note**: When mutagen exceptions occur, they are wrapped in `FileCorruptedError` with exception chaining, so you can access the original exception via `exception.__cause__` if needed for debugging.
