# Writing Metadata Guide

This guide covers all aspects of writing metadata to audio files, including writing strategies, format handling, and unsupported field management.

## Table of Contents

- [Overview](#overview)
- [Basic Writing](#basic-writing)
- [Metadata Dictionary Structure](#metadata-dictionary-structure)
- [Writing Defaults by File Extension](#writing-defaults-by-file-extension)
- [Writing Strategies](#writing-strategies)
- [Unsupported Metadata Handling](#unsupported-metadata-handling)
- [Advanced Examples](#advanced-examples)

## Overview

The `update_metadata()` function provides a flexible way to write metadata to audio files with support for multiple formats, strategies, and error handling modes.

**For validation before writing**, see the [Pre-Update Validation section in README.md](../README.md#pre-update-validation-api-reference).

## Basic Writing

```python
from audiometa import update_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

# Basic metadata update (recommended: use UnifiedMetadataKey constants)
update_metadata("song.mp3", {
    UnifiedMetadataKey.TITLE: 'New Title',
    UnifiedMetadataKey.ARTISTS: ['Artist Name'],
    UnifiedMetadataKey.RATING: 85
})
```

## Metadata Dictionary Structure

When writing, metadata should be provided as a dictionary with keys corresponding to unified metadata fields defined in `UnifiedMetadataKey`.

```python
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

metadata = {
    UnifiedMetadataKey.TITLE: 'Song Title',
    UnifiedMetadataKey.ARTISTS: ['Artist 1', 'Artist 2'],
    UnifiedMetadataKey.ALBUM: 'Album Name',
    UnifiedMetadataKey.RELEASE_DATE: '2024',
    UnifiedMetadataKey.GENRES_NAMES: ['Rock'],
    UnifiedMetadataKey.RATING: 85,
    UnifiedMetadataKey.BPM: 120,
    UnifiedMetadataKey.COMMENT: 'Some comments here',
}
```

## Writing Defaults by File Extension

The library automatically selects appropriate default metadata formats based on file extension:

### MP3 Files (ID3v2)

- **Default Format**: ID3v2.4
- **Why ID3v2.4?**: Most compatible with modern software and supports Unicode
- **Fallback**: If ID3v2.4 writing fails, automatically falls back to ID3v2.3

### FLAC Files (Vorbis Comments)

- **Default Format**: Vorbis Comments
- **Why Vorbis?**: Native format for FLAC files, full Unicode support

### WAV Files (RIFF INFO)

- **Default Format**: RIFF INFO chunks
- **Why RIFF?**: Native format for WAV files, widely supported

### ID3v2 Version Selection

When writing to MP3 files, the library intelligently selects the best ID3v2 version:

```python
from audiometa import update_metadata
from audiometa.utils.metadata_format import MetadataFormat

# The library automatically chooses ID3v2.3 for MP3 files for best compatibility
update_metadata("song.mp3", {"title": "Song Title"})

# You can override the version if needed
update_metadata("song.mp3", {"title": "Song Title"},
                metadata_format=MetadataFormat.ID3V2_4)  # Force ID3v2.4

# Or specify version with id3v2_version parameter
update_metadata("song.mp3", {"title": "Song Title"},
                id3v2_version=(2, 4, 0))  # ID3v2.4
```

**Note**: The `id3v2_version` parameter lets you choose which ID3v2 version to target (e.g., `(2, 3, 0)` for ID3v2.3, `(2, 4, 0)` for ID3v2.4). This affects how multi-value fields and certain metadata are written.

## Writing Strategies

The library provides flexible control over how metadata is written to files that may already contain metadata in other formats.

### Available Strategies

1. **`SYNC` (Default)**: Write to native format and synchronize other metadata formats that are already present
2. **`PRESERVE`**: Write to native format only, preserve existing metadata in other formats
3. **`CLEANUP`**: Write to native format and remove all non-native metadata formats
4. **`FORCE`**: Write only to the specified format (when `metadata_format` is provided), fail on unsupported fields

### Strategy Details

#### SYNC Strategy (Default)

Writes metadata to the native format and synchronizes other metadata formats that are already present. This provides the best user experience by writing metadata where possible and handling unsupported fields gracefully. For each format, unsupported fields are filtered out with individual warnings, while all supported fields are synced successfully.

- **MP3 files**: Writes to ID3v2 and syncs other formats (ID3v1 if present)
- **FLAC files**: Writes to Vorbis comments and syncs other formats (ID3v1, ID3v2 if present)
- **WAV files**: Writes to RIFF and syncs other formats (ID3v1, ID3v2 if present)

```python
from audiometa import update_metadata
from audiometa.utils.metadata_writing_strategy import MetadataWritingStrategy

# SYNC strategy (default) - synchronize all existing formats
update_metadata("song.wav", {"title": "New Title"},
                metadata_strategy=MetadataWritingStrategy.SYNC)

# Result:
# - RIFF tags: Synchronized with new metadata (native format)
# - ID3v2 tags: Synchronized with new metadata (if present)
# - ID3v1 tags: Synchronized with new metadata (if present)
# - When reading: RIFF title is returned (highest precedence)
# Note: SYNC preserves and updates ALL existing metadata formats
```

**Example with unsupported fields**:

```python
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

# WAV file with existing ID3v1 tags (30-char limit and no album artist support)
update_metadata("song.wav", {
    UnifiedMetadataKey.TITLE: "This is a Very Long Title That Exceeds ID3v1 Limits",
    UnifiedMetadataKey.ALBUM_ARTISTS: ["Various Artists"]
})

# Result:
# - RIFF tags: Updated with full title and album artist
# - ID3v1 tags: Synchronized with truncated 30-char title, album artist skipped (not supported)
# - Warnings: "Field ALBUM_ARTISTS not supported by ID3V1 format, skipped"
# - When reading: RIFF title is returned (higher precedence) and album artist is available
```

#### PRESERVE Strategy

Writes to native format only, preserves existing metadata in other formats.

```python
from audiometa import update_metadata
from audiometa.utils.metadata_writing_strategy import MetadataWritingStrategy

# PRESERVE strategy - keep other formats unchanged
update_metadata("song.wav", {"title": "New Title"},
                metadata_strategy=MetadataWritingStrategy.PRESERVE)

# Result:
# - RIFF tags: Updated with new metadata
# - ID3v2 tags: Preserved (not modified)
# - ID3v1 tags: Preserved (not modified)
```

#### CLEANUP Strategy

Writes to native format and removes all non-native metadata formats.

```python
from audiometa import update_metadata
from audiometa.utils.metadata_writing_strategy import MetadataWritingStrategy

# CLEANUP strategy - remove non-native formats
update_metadata("song.wav", {"title": "New Title"},
                metadata_strategy=MetadataWritingStrategy.CLEANUP)

# Result:
# - RIFF tags: Updated with new metadata
# - ID3v2 tags: Removed completely
# - ID3v1 tags: Removed completely
# - When reading: Only RIFF metadata available
```

#### FORCE Strategy (Format-Specific Writing)

Write only to the specified format (when `metadata_format` is provided). This always fails fast for unsupported fields.

```python
from audiometa import update_metadata
from audiometa.utils.metadata_format import MetadataFormat

# Write specifically to ID3v1 format
update_metadata("song.flac", {"title": "New Title"},
                metadata_format=MetadataFormat.ID3V1)

# Write specifically to ID3v2 format (even for WAV files)
update_metadata("song.wav", {"title": "New Title"},
                metadata_format=MetadataFormat.ID3V2)

# Write specifically to RIFF format
update_metadata("song.wav", {"title": "New Title"},
                metadata_format=MetadataFormat.RIFF)

# Write specifically to Vorbis format
update_metadata("song.flac", {"title": "New Title"},
                metadata_format=MetadataFormat.VORBIS)
```

## Unsupported Metadata Handling

The library handles unsupported metadata consistently across all strategies:

### Behavior by Strategy and Configuration

- **FORCE strategy** (when `metadata_format` is specified): Always fails fast by raising `MetadataFieldNotSupportedByMetadataFormatError` for any unsupported field. **No writing is performed** - the file remains completely unchanged.

- **All strategies (SYNC, PRESERVE, CLEANUP) with `fail_on_unsupported_field=False` (default)**: Handle unsupported fields gracefully by logging individual warnings for each unsupported field and continuing with supported fields. For SYNC strategy, unsupported fields are filtered per-format, allowing all supported fields to sync to each format.

- **All strategies (SYNC, PRESERVE, CLEANUP) with `fail_on_unsupported_field=True`**: Fails fast if any field is not supported by the target format. **No writing is performed** - the file remains completely unchanged (atomic operation).

### Format-Specific Limitations

| Format         | FORCE Strategy                    | Strategies with `fail_on_unsupported_field=False`                     | Strategies with `fail_on_unsupported_field=True`  |
| -------------- | --------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------- |
| **RIFF (WAV)** | Always fails fast, **no writing** | Logs individual warnings per unsupported field, writes supported ones | Fails fast for unsupported fields, **no writing** |
| **ID3v1**      | Always fails fast, **no writing** | Logs individual warnings per unsupported field, writes supported ones | Fails fast for unsupported fields, **no writing** |
| **ID3v2**      | Always fails fast, **no writing** | All fields supported                                                  | All fields supported                              |
| **Vorbis**     | Always fails fast, **no writing** | All fields supported                                                  | All fields supported                              |

### Atomic Write Operations

When `fail_on_unsupported_field=True` is used, the library ensures **atomic write operations**:

- **All-or-nothing behavior**: Either all metadata is written successfully, or nothing is written at all
- **File integrity**: If any field is unsupported, the file remains completely unchanged
- **No partial updates**: Prevents inconsistent metadata states where only some fields are updated
- **Error safety**: Ensures that failed operations don't leave files in a partially modified state

## Advanced Examples

### Example: Handling Unsupported Metadata

```python
from audiometa import update_metadata, get_unified_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.metadata_writing_strategy import MetadataWritingStrategy
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

# All strategies - handle unsupported fields gracefully with warnings
update_metadata("song.wav", {
    UnifiedMetadataKey.TITLE: "Song",
    UnifiedMetadataKey.RATING: 85,
    UnifiedMetadataKey.BPM: 120  # Not supported by RIFF
})
# Result: Writes title and rating to RIFF, logs warning about BPM, continues

update_metadata("song.wav", {
    UnifiedMetadataKey.TITLE: "Song",
    UnifiedMetadataKey.RATING: 85,
    UnifiedMetadataKey.BPM: 120
}, metadata_strategy=MetadataWritingStrategy.PRESERVE)
# Result: Writes title and rating to RIFF, logs warning about BPM, preserves other formats

update_metadata("song.wav", {
    UnifiedMetadataKey.TITLE: "Song",
    UnifiedMetadataKey.RATING: 85,
    UnifiedMetadataKey.BPM: 120
}, metadata_strategy=MetadataWritingStrategy.CLEANUP)
# Result: Writes title and rating to RIFF, logs warning about BPM, removes other formats

# FORCE strategy - always fails fast for unsupported fields, no writing performed
try:
    update_metadata("song.wav", {
        UnifiedMetadataKey.TITLE: "Song",
        UnifiedMetadataKey.RATING: 85,
        UnifiedMetadataKey.BPM: 120
    }, metadata_format=MetadataFormat.RIFF)
except MetadataFieldNotSupportedByMetadataFormatError as e:
    print(f"BPM not supported in RIFF format: {e}")
    # File remains completely unchanged - no metadata was written

# Strategies with fail_on_unsupported_field=True - atomic operation, no writing on failure
try:
    update_metadata("song.wav", {
        UnifiedMetadataKey.TITLE: "Song",
        UnifiedMetadataKey.RATING: 85,
        UnifiedMetadataKey.BPM: 120
    }, metadata_strategy=MetadataWritingStrategy.SYNC,
       fail_on_unsupported_field=True)
except MetadataFieldNotSupportedByMetadataFormatError as e:
    print(f"BPM not supported: {e}")
    # File remains completely unchanged - no metadata was written (atomic operation)
```

### Example: Demonstrating Atomic Behavior

```python
from audiometa import get_unified_metadata, update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

# File with existing metadata
original_metadata = get_unified_metadata("song.wav")
print(f"Original title: {original_metadata.get(UnifiedMetadataKey.TITLE)}")  # e.g., "Original Title"

# Attempt to write metadata with unsupported field
try:
    update_metadata("song.wav", {
        UnifiedMetadataKey.TITLE: "New Title",      # This would be supported
        UnifiedMetadataKey.RATING: 85,              # This would be supported
        UnifiedMetadataKey.BPM: 120                 # This is NOT supported by RIFF format
    }, fail_on_unsupported_field=True)
except MetadataFieldNotSupportedByMetadataFormatError:
    pass

# Verify file is unchanged (atomic behavior)
final_metadata = get_unified_metadata("song.wav")
print(f"Final title: {final_metadata.get(UnifiedMetadataKey.TITLE)}")  # Still "Original Title" - no changes made
```

### Example: Strategy-Based Writing with ID3v2 Version

```python
from audiometa import update_metadata
from audiometa.utils.metadata_writing_strategy import MetadataWritingStrategy
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

# Use SYNC strategy and specify ID3v2 version
update_metadata(
    "song.mp3",
    {
        UnifiedMetadataKey.TITLE: "New Title",
        UnifiedMetadataKey.ARTISTS: ["Artist Name"]
    },
    metadata_strategy=MetadataWritingStrategy.SYNC,
    id3v2_version=(2, 4, 0)
)
```

## Related Documentation

- [Metadata Field Guide](METADATA_FIELD_GUIDE.md) - Comprehensive field support reference
- [Error Handling Guide](ERROR_HANDLING_GUIDE.md) - Exception handling documentation
- [Pre-Update Validation](../README.md#pre-update-validation-api-reference) - Validation before writing
