<p align="center">
  <img src="assets/logo.png" alt="AudioMeta Logo" width="200"/>
</p>

# AudioMeta Python

[![CI](https://github.com/Andreas-Garcia/audiometa/actions/workflows/ci.yml/badge.svg)](https://github.com/Andreas-Garcia/audiometa/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/audiometa-python)](https://pypi.org/project/audiometa-python/)
[![PyPI downloads/month](https://img.shields.io/pypi/dm/audiometa-python?cacheSeconds=86400)](https://pypi.org/project/audiometa-python/)
[![PyPI downloads/week](https://img.shields.io/pypi/dw/audiometa-python?cacheSeconds=86400)](https://pypi.org/project/audiometa-python/)
[![Version](https://img.shields.io/badge/version-0.2.6-orange)](https://github.com/Andreas-Garcia/audiometa)

A powerful, unified Python library for reading and writing audio metadata across multiple formats. AudioMeta supports MP3, FLAC, and WAV audio files, working seamlessly with ID3v1, ID3v2, Vorbis, and RIFF metadata formats through a single, consistent API.

**Author**: [Andreas Garcia](https://github.com/Andreas-Garcia)

## Table of Contents

- [Features](#features)
- [Supported Formats](#supported-formats)
  - [Supported Audio Formats Per Metadata Format](#supported-audio-formats-per-metadata-format)
  - [Supported Metadata Formats per Audio Format](#supported-metadata-formats-per-audio-format)
  - [Format Capabilities](#format-capabilities)
- [Supported Fields And Audio Technical Info](#supported-fields-and-audio-technical-info)
- [Installation](#installation)
  - [System Requirements](#system-requirements)
  - [Installing Required Tools](#installing-required-tools)
  - [Verifying Installation](#verifying-installation)
  - [External Tools Usage](#external-tools-usage)
- [Getting Started](#getting-started)
  - [What You Need](#what-you-need)
  - [Your First Steps](#your-first-steps)
  - [Common Use Cases](#common-use-cases)
- [Quick Start](#quick-start)
  - [Reading Metadata](#reading-metadata)
  - [Validate Metadata Before Update](#validate-metadata-before-update)
  - [Writing Metadata](#writing-metadata)
  - [Deleting Metadata](#deleting-metadata)
- [Core API Reference](#core-api-reference)
  - [Reading Metadata (API Reference)](#reading-metadata-api-reference)
  - [Pre-Update Validation (API Reference)](#pre-update-validation-api-reference)
  - [Writing Metadata (API Reference)](#writing-metadata-api-reference)
  - [Deleting Metadata (API Reference)](#deleting-metadata-api-reference)
  - [Error Handling (API Reference)](#error-handling-api-reference)
- [Metadata Guide](#metadata-guide)
  - [Metadata Field Guide: Support and Handling](#metadata-field-guide-support-and-handling)
  - [Audio Technical Info Guide](#audio-technical-info-guide)
  - [Unsupported Metadata Handling](#unsupported-metadata-handling)
- [Command Line Interface](#command-line-interface)
  - [Installation](#cli-installation)
  - [Basic Usage](#basic-usage)
  - [Advanced Options](#advanced-options)
  - [Output Formats](#output-formats)
  - [Examples](#examples)
- [Requirements](#requirements)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](https://github.com/Andreas-Garcia/audiometa/security/policy)
- [License](#license)

## Features

- **Unified API**: A single, consistent API for reading and writing metadata across all supported formats. Use the same functions (`get_unified_metadata()`, `update_metadata()`, etc.) regardless of whether you're working with MP3, FLAC, or WAV files. The library automatically handles format-specific differences, normalizes field names, and intelligently merges metadata from multiple formats when reading.

- **Multi-format Support**: ID3v1, ID3v2, Vorbis (FLAC), and RIFF (WAV) metadata formats. Many audio files can contain multiple metadata formats simultaneously (e.g., MP3 files with both ID3v1 and ID3v2 tags, FLAC files with ID3v1, ID3v2, and Vorbis comments). AudioMeta intelligently handles these scenarios with automatic format detection and priority-based reading.

- **Format Control**: Force specific metadata formats when reading or writing for precise control. Read only ID3v1 tags from an MP3 file that contains both ID3v1 and ID3v2, or write metadata exclusively to the Vorbis format in a FLAC file. Essential for format-specific operations, migration tasks, or working with legacy metadata formats.

- **Technical Information**: Access to technical information about audio files, including duration, bitrate, sample rate, channels, and file size. This technical data is extracted directly from audio file headers, so you can get comprehensive file analysis even when no metadata tags are present.

- **Comprehensive Metadata Fields**: Support for 15+ metadata fields including title, artist, album, rating, BPM, and more. More fields are planned to be supported soon.

- **Read/Write Operations**: Full read and write support for most formats

- **Rating Support**: Normalized rating handling across different formats

- **Complete File Analysis**: Get full metadata including headers and technical details even when no metadata is present

- **Error Handling**: Robust error handling with specific exception types

- **Type Hints**: Full type annotation support for better IDE integration

- **Cross-platform**: Works on Windows, macOS, and Linux (requires ffprobe and flac tools for full functionality)

- **Extensive Testing**: Comprehensive test coverage with 500+ tests

**Note**: OGG file support is planned but not yet implemented.

## Supported Formats

### Supported Audio Formats Per Metadata Format

| Format | Audio Format   |
| ------ | -------------- |
| ID3v1  | MP3, FLAC, WAV |
| ID3v2  | MP3, FLAC, WAV |
| Vorbis | FLAC           |
| RIFF   | WAV            |

### Supported Metadata Formats per Audio Format

| Audio Format | Supported Metadata Formats |
| ------------ | -------------------------- |
| MP3          | ID3v1, ID3v2               |
| FLAC         | ID3v1, ID3v2, Vorbis       |
| WAV          | ID3v1, ID3v2, RIFF         |

### Format Capabilities

#### ID3v1 Metadata Format

- **Primary Support**: MP3 files (native format)
- **Extended Support**: FLAC and WAV files with ID3v1 tags
- **Limitations**: 30-character field limits, no album artist support
- **Operations**: Full read/write support with direct file manipulation
- **Note**: ID3v1.1 is supported (track number supported in comment field)

#### ID3v2 Metadata Format

- **Supported Formats**: MP3, WAV, FLAC
- **Features**: All metadata fields, multiple artists, cover art, extended metadata
- **Versions**: Supports ID3v2.3 and ID3v2.4
- **Note**: Most versatile format, works across multiple file types

#### Vorbis Metadata Format

- **Primary Support**: FLAC files (native Vorbis comments)
- **Features**: Most metadata fields, multiple artists, cover art
- **Limitations**: Some fields not supported (lyrics, etc.)
- **Note**: Standard metadata format for FLAC files

**Vorbis Comment Key Handling**
Vorbis comment field names are case-insensitive, as defined by the Xiph.org Vorbis Comment specification.
To ensure consistent and predictable behavior, this library normalizes all field names internally and follows modern interoperability conventions.

**_Reading_**
When reading Vorbis comments, the library treats field names in a case-insensitive manner. For example, "TITLE", "title", and "Title" are considered equivalent.

**_Writing_**
When writing Vorbis comments, the library standardizes field names to uppercase to maintain consistency and compatibility with common practices in audio metadata management. It thus writes "TITLE" removing eventual existing variations in casing.

#### RIFF Metadata Format

- **Strict Support**: WAV files only
- **Features**: Most metadata fields including album artist, language, comments
- **Limitations**: Some fields not supported (BPM, lyrics, etc.)
- **Note**: Native metadata format for WAV files

## Supported Fields And Audio Technical Info

AudioMeta supports comprehensive audio information across all formats. For technical audio information (duration, bitrate, sample rate, channels, file size, format info, MD5 checksum validation and repair), see:

**[Audio Technical Info Guide](docs/AUDIO_TECHNICAL_INFO_GUIDE.md)**

For metadata fields (title, artist, album, genres, ratings, etc.), see:

**[Metadata Field Guide: Support and Handling](docs/METADATA_FIELD_GUIDE.md)**

## Installation

```bash
pip install audiometa-python
```

### System Requirements

- **Python**: 3.12 or higher
- **Operating Systems**: Windows, macOS, Linux
- **Dependencies**: Automatically installed with the package
- **Required Tools**: ffprobe (for WAV file processing), flac (for FLAC MD5 validation)

### Installing Required Tools

The library requires several external tools for full functionality. **Use the automated installation scripts** to ensure you have the correct pinned versions that match CI.

#### Automated Setup {#automated-setup-recommended}

To ensure your local environment matches CI exactly, use the automated installation scripts:

```bash
# Ubuntu/Linux
./scripts/install-system-dependencies-ubuntu.sh

# macOS
./scripts/install-system-dependencies-macos.sh

# Windows
.\scripts\install-system-dependencies-windows.ps1
```

These scripts install all required tools with pinned versions that match CI:

**Production tools (required for library functionality):**

- **ffmpeg** / **ffprobe** - For WAV file processing and technical info (all platforms)
- **flac** / **metaflac** - For FLAC MD5 validation and metadata writing (all platforms)
- **id3v2** - For ID3v2 tag writing on FLAC files (Ubuntu/macOS only; Windows requires WSL)
- **bwfmetaedit** - For BWF metadata (Ubuntu/macOS/Windows)
- **libsndfile** - For audio file I/O (Ubuntu/macOS only)

**Dev/testing tools (only needed for running tests locally):**

- **mediainfo** - Only for integration test verification
- **exiftool** - Only for integration test verification

**Pinned versions:** All tool versions are pinned in separate configuration files (the single source of truth):

- [`system-dependencies-prod.toml`](system-dependencies-prod.toml) - Production dependencies (ffmpeg, flac, id3v2)
- [`system-dependencies-test-only.toml`](system-dependencies-test-only.toml) - Test-only dependencies (mediainfo, exiftool, bwfmetaedit, libsndfile) - supplementary to prod dependencies
- [`system-dependencies-lint.toml`](system-dependencies-lint.toml) - Lint dependencies (PowerShell)

The scripts verify installed versions match these pinned versions. See the configuration files for complete details and OS-specific version information.

**Note for Windows users:**

- The `id3v2` tool is not available as a native Windows binary. The installation script attempts to use **WSL (Windows Subsystem for Linux)** to install `id3v2` via Ubuntu's package manager, but WSL installation complexity (requiring system restarts, DISM configuration, and Ubuntu distribution setup) has prevented successful full installation in practice. This is why Windows CI only runs e2e tests (which don't require `id3v2`). For local development, the script will attempt WSL installation, but manual WSL setup may be required.
- **Windows CI differences:** Windows CI only runs e2e tests (not unit/integration tests), so some tools are skipped in CI but still installed locally for full test coverage: `mediainfo` and `exiftool` are required for integration tests and are installed by the script for local development, but skipped in Windows CI since integration tests don't run there.

#### Verifying Installation

After installation, verify the tools are available:

```bash
ffprobe -version
flac --version
```

The installation scripts automatically verify installed versions match pinned versions from `system-dependencies-prod.toml`, `system-dependencies-test-only.toml`, and `system-dependencies-lint.toml`.

#### External Tools Usage

AudioMeta uses a combination of Python libraries and external command-line tools depending on the operation and audio format. This section provides a comprehensive overview of when external tools are required versus when pure Python libraries are used.

| Format     | Read Metadata    | Write Metadata                             | Technical Info (Duration/Bitrate/etc.) | Validation           |
| ---------- | ---------------- | ------------------------------------------ | -------------------------------------- | -------------------- |
| **ID3v1**  | Custom (Python)  | Custom (Python)                            | mutagen (Python)                       | N/A                  |
| **ID3v2**  | mutagen (Python) | mutagen (Python) / id3v2/mid3v2 (external) | mutagen (Python)                       | N/A                  |
| **Vorbis** | Custom (Python)  | metaflac (external)                        | mutagen (Python)                       | flac (external tool) |
| **RIFF**   | mutagen (Python) | Custom (Python)                            | ffprobe (external tool)                | N/A                  |

**Notes:**

- **ID3v2**: Uses external tools (`id3v2` or `mid3v2`) for writing to FLAC files to prevent file corruption
- **Vorbis**: Uses `metaflac` external tool for writing to preserve proper uppercase key casing and avoid file corruption
- **External tools required**: `metaflac`, `id3v2`/`mid3v2` (for FLAC files), `ffprobe`, `flac`

## Getting Started

### What You Need

- Python 3.12+
- Audio files (MP3, FLAC, WAV)
- Basic Python knowledge

### Your First Steps

1. **Install the library** using pip
2. **Try reading metadata** from an existing audio file
3. **Update some metadata** to see how writing works
4. **Explore advanced features** like format-specific operations

### Common Use Cases

- **Music library management**: Organize and clean up metadata
- **Metadata cleanup**: Remove unwanted or duplicate information
- **Format conversion**: Migrate metadata between formats
- **Batch processing**: Update multiple files at once
- **Privacy protection**: Remove personal information from files

## Quick Start

### Reading Metadata

When reading metadata, there are three functions to use: `get_unified_metadata` and `get_unified_metadata_field`, and `get_full_metadata`.

- `get_unified_metadata`: Reads all metadata from a file and returns a unified dictionary.
- `get_unified_metadata_field`: Reads a specific metadata field from a file.
- `get_full_metadata`: Reads all metadata from a file and returns a dictionary including headers and technical info.

#### Reading from a specific metadata format

The library supports reading metadata from specific formats (ID3v1, ID3v2.3, ID3v2.4, Vorbis, RIFF). This is useful when you know the format of the file you are working with and you want to read only from that format.

```python
from audiometa import get_unified_metadata, UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat

metadata = get_unified_metadata("path/to/your/audio.mp3", metadata_format=MetadataFormat.ID3V2)
print(f"Title: {metadata.get(UnifiedMetadataKey.TITLE, 'Unknown')}")
```

When specifying a metadata format not supported by the audio format of the file, raises a MetadataFormatNotSupportedByAudioFormatError.

```python
from audiometa import get_unified_metadata, UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.exceptions import MetadataFormatNotSupportedByAudioFormatError

try:
    metadata = get_unified_metadata("path/to/your/audio.mp3", metadata_format=MetadataFormat.RIFF)
except MetadataFormatNotSupportedByAudioFormatError as e:
    print(f"Error: {e}")
```

#### Reading All Metadata

**`get_unified_metadata(file_path, metadata_format=None)`**

Reads all metadata from a file and returns a unified dictionary.
If `metadata_format` is specified, reads only from that format.
If not specified, uses priority order across all formats.

**Note:** `file_path` can be a string or `pathlib.Path` object.

```python
from audiometa import get_unified_metadata

metadata = get_unified_metadata("path/to/your/audio.mp3")
print(f"Title: {metadata.get(UnifiedMetadataKey.TITLE, 'Unknown')}")
print(f"Artist: {metadata.get(UnifiedMetadataKey.ARTISTS, ['Unknown'])}")
print(f"Album: {metadata.get(UnifiedMetadataKey.ALBUM, 'Unknown')}")
```

#### Reading Specific Metadata Fields (Quick Start)

**`get_unified_metadata_field(file_path, field, metadata_format=None)`**

Reads a specific metadata field. If no metadata format is specified, uses priority order across all formats.

**Note:** `file_path` can be a string or `pathlib.Path` object.

**Note:** The `field` parameter can be a `UnifiedMetadataKey` enum instance or a string matching an enum value (e.g., `"title"`). Invalid values will raise `MetadataFieldNotSupportedByLibError`.

```python
from audiometa import get_unified_metadata_field, UnifiedMetadataKey

# Get title using priority order (all formats)
title = get_unified_metadata_field("song.mp3", UnifiedMetadataKey.TITLE)
```

If `metadata_format` is specified, reads only from that format.

```python
from audiometa import get_unified_metadata_field, UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat

# Get raw rating from specific format only
id3v2_rating = get_unified_metadata_field("song.mp3", UnifiedMetadataKey.RATING, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0))
```

If `metadata_format` is specified and the field is not supported by that format, raises a MetadataFieldNotSupportedError.

```python
from audiometa import get_unified_metadata_field, UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError

# Attempt to get unsupported field from specific format

try:
    riff_bpm = get_unified_metadata_field("song.wav", UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.RIFF)
except MetadataFieldNotSupportedByMetadataFormatError as e:
    print(f"Error: {e}")
```

#### Reading Full Metadata From All Formats Including Headers and Technical Info

**`get_full_metadata(file_path, include_headers=True, include_technical=True)`**

Gets comprehensive metadata including all available information from a file, including headers and technical details even when no metadata is present.

**Note:** `file_path` can be a string or `pathlib.Path` object.

```python
from audiometa import get_full_metadata

full_metadata = get_full_metadata("song.mp3")
```

### Validate Metadata Before Update

Before updating metadata in a file, it's recommended to validate your metadata to catch errors early:

```python
from audiometa import validate_metadata_for_update, UnifiedMetadataKey

# Validate metadata before updating
metadata = {
    UnifiedMetadataKey.TITLE: 'New Song Title',
    UnifiedMetadataKey.ARTISTS: ['Artist Name'],
    UnifiedMetadataKey.ALBUM: 'Album Name',
    UnifiedMetadataKey.RATING: 85,
}

try:
    validate_metadata_for_update(metadata)
    print("Metadata is valid!")
except Exception as e:
    print(f"Metadata validation failed: {e}")
```

This validation checks for:

- **Type correctness**: Ensures values match expected types (strings for title, lists for artists, etc.)
- **Format rules**: Validates field formats (e.g., release dates must be in ISO 8601 format)
- **Value ranges**: Checks ratings, track numbers, and other numeric values are within valid ranges
- **Empty values**: Verifies at least one field is provided

See [Pre-Update Validation Function](#pre-update-validation-function) for detailed validation rules and examples.

### Writing Metadata

```python
from audiometa import update_metadata

# Update metadata (use UnifiedMetadataKey for explicit typing)
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey

new_metadata = {
    UnifiedMetadataKey.TITLE: 'New Song Title',
    UnifiedMetadataKey.ARTISTS: ['Artist Name'],
    UnifiedMetadataKey.ALBUM: 'Album Name',
    UnifiedMetadataKey.RATING: 85,
}
update_metadata("path/to/your/audio.mp3", new_metadata)
```

**Format-specific Writing**

```python
from audiometa.utils.MetadataFormat import MetadataFormat
update_metadata("song.wav", new_metadata, metadata_format=MetadataFormat.RIFF)
```

### Deleting Metadata

There are two ways to remove metadata from audio files:

#### Delete All Metadata (Complete Removal)

```python
from audiometa import delete_all_metadata

# Delete ALL metadata from ALL supported formats (removes metadata headers entirely)
success = delete_all_metadata("path/to/your/audio.mp3")
print(f"All metadata deleted: {success}")

# Delete metadata from specific format only
from audiometa.utils.MetadataFormat import MetadataFormat
success = delete_all_metadata("song.wav", metadata_format=MetadataFormat.ID3V2)
# This removes only ID3v2 tags, keeps RIFF metadata
```

**Important**: This function removes the metadata headers/containers entirely from the file, not just the content. This means:

- ID3v2 tag structure is completely removed
- Vorbis comment blocks are completely removed
- RIFF INFO chunks are completely removed
- File size is significantly reduced

#### Remove Specific Fields (Selective Removal)

```python
from audiometa import update_metadata, UnifiedMetadataKey

# Remove only specific fields by setting them to None
update_metadata("path/to/your/audio.mp3", {
    UnifiedMetadataKey.TITLE: None,        # Remove title field
    UnifiedMetadataKey.ARTISTS: None # Remove artist field
    # Other fields remain unchanged
})

# This removes only the specified fields while keeping:
# - Other metadata fields intact
# - Metadata headers/containers in place
# - File size mostly unchanged
```

**When to use each approach:**

- **`delete_all_metadata()`**: When you want to completely strip all metadata from a file
- **Setting fields to `None`**: When you want to clean up specific fields while preserving others

#### Comparison Table

| Aspect               | `delete_all_metadata()`   | Setting fields to `None`      |
| -------------------- | ------------------------- | ----------------------------- |
| **Scope**            | Removes ALL metadata      | Removes only specified fields |
| **Metadata headers** | **Completely removed**    | **Preserved**                 |
| **File size**        | Significantly reduced     | Minimal change                |
| **Other fields**     | All removed               | Unchanged                     |
| **Use case**         | Complete cleanup          | Selective cleanup             |
| **Performance**      | Faster (single operation) | Slower (field-by-field)       |

#### Example Scenarios

**Scenario 1: Complete Privacy Cleanup**

```python
# Remove ALL metadata for privacy
delete_all_metadata("personal_recording.mp3")
# Result: File has no metadata headers at all (ID3v2 tags completely removed)
```

**Scenario 2: Clean Up Specific Information**

```python
# Remove only personal info, keep technical metadata
update_metadata("song.mp3", {
    UnifiedMetadataKey.TITLE: None,           # Remove title
    UnifiedMetadataKey.ARTISTS: None,   # Remove artist
    # Keep album, genre, year, etc.
})
# Result: File keeps metadata headers but removes specific fields
```

### Getting Technical Information

The library provides functional APIs for getting technical information about audio files:

```python
from audiometa import get_duration_in_sec, get_bitrate, get_sample_rate, get_channels, get_file_size

# Get technical information using functional API (recommended)
duration = get_duration_in_sec("path/to/your/audio.flac")
bitrate = get_bitrate("path/to/your/audio.flac")
sample_rate = get_sample_rate("path/to/your/audio.flac")
channels = get_channels("path/to/your/audio.flac")
file_size = get_file_size("path/to/your/audio.flac")

print(f"Duration: {duration} seconds")
print(f"Bitrate: {bitrate} kbps")
print(f"Sample Rate: {sample_rate} Hz")
print(f"Channels: {channels}")
print(f"File Size: {file_size} bytes")
```

## Core API Reference

### Reading Metadata (API Reference)

#### Reading Priorities (Tag Precedence)

When the same metadata tag exists in multiple formats within the same file, the library follows file-specific precedence orders for reading:

#### FLAC Files Reading Priorities

1. **Vorbis** (highest precedence)
2. **ID3v2**
3. **ID3v1** (lowest precedence, legacy format)

#### MP3 Files Reading Priorities

1. **ID3v2** (highest precedence)
2. **ID3v1** (lowest precedence, legacy format)

#### WAV Files Reading Priorities

1. **RIFF** (highest precedence)
2. **ID3v2**
3. **ID3v1** (lowest precedence, legacy format)

**Examples**:

- For MP3 files: If a title exists in both ID3v1 and ID3v2, the ID3v2 title will be returned.
- For WAV files: If a title exists in both RIFF and ID3v2, the RIFF title will be returned.
- For FLAC files: If a title exists in both Vorbis and ID3v2, the Vorbis title will be returned.

#### Reading All Metadata From All Metadata Formats Including Priority Logic

**`get_unified_metadata(file_path, metadata_format=None)`**

Reads all metadata from a file and returns a unified dictionary.
If `metadata_format` is specified, reads only from that format.
If not specified, uses priority order across all formats.

**Note:** `file_path` can be a string or `pathlib.Path` object.

```python
from audiometa import get_unified_metadata

# Read all metadata (unified across all formats)
metadata = get_unified_metadata("song.mp3")
print(metadata[UnifiedMetadataKey.TITLE])  # Song title
print(metadata[UnifiedMetadataKey.ARTISTS])  # List of artists
```

#### Reading All Metadata From A Specific Format

**`get_unified_metadata(file_path, metadata_format=MetadataFormat.ID3V2)`**

```python

# Read only ID3v2 metadata
from audiometa.utils.MetadataFormat import MetadataFormat
id3v2_metadata = get_unified_metadata("song.mp3", metadata_format=MetadataFormat.ID3V2)

# Read only Vorbis metadata
vorbis_metadata = get_unified_metadata("song.flac", metadata_format=MetadataFormat.VORBIS)
```

#### Reading All Metadata From A ID3v2 Format With Version

**`get_unified_metadata(file_path, metadata_format=MetadataFormat.ID3V2), id3v2_version=(2, 3, 0))`**

```python

# Read only ID3v2.3 metadata
from audiometa.utils.MetadataFormat import MetadataFormat
id3v2_3_metadata = get_unified_metadata("song.mp3", metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0))

# Read only ID3v2.4 metadata
id3v2_4_metadata = get_unified_metadata("song.mp3", metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0))
```

#### Reading Specific Metadata Fields

**`get_unified_metadata_field(file_path, field, metadata_format=None)`**

Reads a specific metadata field. If `metadata_format` is specified, reads only from that format; otherwise uses priority order across all formats.

**Note:** `file_path` can be a string or `pathlib.Path` object.

```python
from audiometa import get_unified_metadata_field, UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat

# Get title using priority order (all formats)
title = get_unified_metadata_field("song.mp3", UnifiedMetadataKey.TITLE)

# Get raw rating from specific format only
id3v2_rating = get_unified_metadata_field("song.mp3", UnifiedMetadataKey.RATING, metadata_format=MetadataFormat.ID3V2)
```

#### Reading Full Metadata From All Formats Including Headers and Technical Info

**`get_full_metadata(file_path, include_headers=True, include_technical=True)`**

Gets comprehensive metadata including all available information from a file, including headers and technical details even when no metadata is present.

**Note:** `file_path` can be a string or `pathlib.Path` object.

This function provides the most complete view of an audio file by combining:

- All metadata from all supported formats (ID3v1, ID3v2, Vorbis, RIFF)
- Technical information (duration, bitrate, sample rate, channels, file size)
- Format-specific headers and structure information
- Raw metadata details from each format

```python
from audiometa import get_full_metadata, UnifiedMetadataKey

# Get complete metadata including headers and technical info
full_metadata = get_full_metadata("song.mp3")

# Access unified metadata (same as get_unified_metadata)
print(f"Title: {full_metadata['unified_metadata'][UnifiedMetadataKey.TITLE]}")
print(f"Artists: {full_metadata['unified_metadata'][UnifiedMetadataKey.ARTISTS]}")

# Access technical information
print(f"Duration: {full_metadata['technical_info']['duration_seconds']} seconds")
print(f"Bitrate: {full_metadata['technical_info']['bitrate_kbps']} kbps")
print(f"Sample Rate: {full_metadata['technical_info']['sample_rate_hz']} Hz")
print(f"Channels: {full_metadata['technical_info']['channels']}")
print(f"File Size: {full_metadata['technical_info']['file_size_bytes']} bytes")

# Access format-specific metadata
print(f"ID3v2 Title: {full_metadata['metadata_format']['id3v2']['title']}")
print(f"Vorbis Title: {full_metadata['metadata_format']['vorbis']['title']}")

# Access header information
print(f"ID3v2 Version: {full_metadata['headers']['id3v2']['version']}")
print(f"ID3v2 Header Size: {full_metadata['headers']['id3v2']['header_size_bytes']}")
print(f"Has ID3v1 Header: {full_metadata['headers']['id3v1']['present']}")
print(f"RIFF Chunk Info: {full_metadata['headers']['riff']['chunk_info']}")

# Access raw metadata details
print(f"Raw ID3v2 Frames: {full_metadata['raw_metadata']['id3v2']['frames']}")
print(f"Raw Vorbis Comments: {full_metadata['raw_metadata']['vorbis']['comments']}")
```

**Parameters:**

- `file_path`: Path to the audio file (str or Path)
- `include_headers`: Whether to include format-specific header information (default: True)
- `include_technical`: Whether to include technical audio information (default: True)

**Returns:**
A comprehensive dictionary containing:

```python
{
    'unified_metadata': {
        # Same as get_unified_metadata() result
        'title': 'Song Title',
        'artists': ['Artist 1', 'Artist 2'],
        'album_name': 'Album Name',
        # ... all other metadata fields
    },
    'technical_info': {
        'duration_seconds': 180.5,
        'bitrate_kbps': 320,
        'sample_rate_hz': 44100,
        'channels': 2,
        'file_size_bytes': 7234567,
        'file_extension': '.mp3',
        'audio_format_name': 'MP3',
        'is_flac_md5_valid': None,  # Only for FLAC files
    },
    'metadata_format': {
        'id3v1': {
            # ID3v1 specific metadata (if present)
            'title': 'Song Title',
            'artist': 'Artist Name',
            # ... other ID3v1 fields
        },
        'id3v2': {
            # ID3v2 specific metadata (if present)
            'title': 'Song Title',
            'artists': ['Artist 1', 'Artist 2'],
            # ... other ID3v2 fields
        },
        'vorbis': {
            # Vorbis specific metadata (if present)
            'title': 'Song Title',
            'artists': ['Artist 1', 'Artist 2'],
            # ... other Vorbis fields
        },
        'riff': {
            # RIFF specific metadata (if present)
            'title': 'Song Title',
            'artist': 'Artist Name',
            # ... other RIFF fields
        }
    },
    'headers': {
        'id3v1': {
            'present': True,
            'position': 'end_of_file',
            'size_bytes': 128,
            'version': '1.1',
            'has_track_number': True
        },
        'id3v2': {
            'present': True,
            'version': '2.3.0',
            'header_size_bytes': 2048,
            'flags': {...},
            'extended_header': {...}
        },
        'vorbis': {
            'present': True,
            'vendor_string': 'reference libFLAC 1.3.2',
            'comment_count': 15,
            'block_size': 4096
        },
        'riff': {
            'present': True,
            'chunk_info': {
                'riff_chunk_size': 7234000,
                'info_chunk_size': 1024,
                'audio_format': 'PCM',
                'subchunk_size': 7232000
            }
        }
    },
    'raw_metadata': {
        'id3v1': {
            'raw_data': b'...',  # Raw 128-byte ID3v1 tag
            'parsed_fields': {...}
        },
        'id3v2': {
            'frames': {...},  # Raw ID3v2 frames
            'raw_header': b'...'
        },
        'vorbis': {
            'comments': {...},  # Raw Vorbis comment blocks
            'vendor_string': '...'
        },
        'riff': {
            'info_chunk': {...},  # Raw RIFF INFO chunk data
            'chunk_structure': {...}
        }
    },
    'format_priorities': {
        'file_extension': '.mp3',
        'reading_order': ['id3v2', 'id3v1'],
        'writing_format': 'id3v2'
    }
}
```

**Use Cases:**

- **Complete file analysis**: Get everything about an audio file in one call
- **Debugging metadata issues**: Inspect raw headers and format-specific data
- **Format migration**: Understand what metadata exists in each format before converting
- **File validation**: Check header integrity and format compliance
- **Metadata forensics**: Analyze metadata structure and detect anomalies
- **Batch processing**: Get comprehensive information for multiple files efficiently

**Examples:**

```python
# Basic usage - get everything
full_info = get_full_metadata("song.mp3")

# Get only metadata without technical details
metadata_only = get_full_metadata("song.mp3", include_technical=False)

# Get only technical info without headers
tech_only = get_full_metadata("song.mp3", include_headers=False)

# Check if file has specific format headers
if full_info['headers']['id3v2']['present']:
    print("File has ID3v2 tags")
    print(f"ID3v2 version: {full_info['headers']['id3v2']['version']}")

# Compare metadata across formats
id3v2_title = full_info['metadata_format']['id3v2'].get('title')
vorbis_title = full_info['metadata_format']['vorbis'].get('title')
if id3v2_title != vorbis_title:
    print("Title differs between ID3v2 and Vorbis")

# Analyze file structure
print(f"File size: {full_info['technical_info']['file_size_bytes']} bytes")
print(f"Metadata overhead: {full_info['headers']['id3v2']['header_size_bytes']} bytes")
print(f"Audio data ratio: {(full_info['technical_info']['file_size_bytes'] - full_info['headers']['id3v2']['header_size_bytes']) / full_info['technical_info']['file_size_bytes'] * 100:.1f}%")
```

### Pre-Update Validation (API Reference)

Before updating metadata, the library provides validation to ensure your data is correct:

**Validation Rules**

The library validates metadata value types and formats when keys are provided as `UnifiedMetadataKey` instances:

- `None` values are allowed and indicate field removal.
- For fields whose expected type is `list[...]` (for example `ARTISTS` or `GENRES_NAMES`) the validator accepts only lists. Each list element is checked against the expected inner type (e.g., `str` for `ARTISTS`).
- For plain types (`str`, `int`, etc.) the value must be an instance of that type.
- On type mismatch the library raises `InvalidMetadataFieldTypeError`.
- **Rating Validation**: See [Rating Validation Rules](#rating-validation-rules) for detailed rules on rating values.
- **Release Date Validation**: See [Release Date Validation Rules](#release-date-validation-rules) for detailed rules on release date formats.

Note: The validator uses the `UnifiedMetadataKey` enum to determine expected types. String keys that match `UnifiedMetadataKey` enum values (e.g., `"title"`, `"artists"`) are automatically converted to enum instances and validated. You can use either string keys or `UnifiedMetadataKey` enum instances - both are validated the same way. Using `UnifiedMetadataKey` enum instances provides better IDE support and type checking.

**`validate_metadata_for_update(unified_metadata, normalized_rating_max_value=None)`**

Validates unified metadata values before updating metadata in a file. Validates that a metadata dictionary contains at least one field and validates types, formats, and values (rating, release date, track number) if present. For detailed validation rules, see [Rating Validation Rules](#rating-validation-rules) and [Release Date Validation Rules](#release-date-validation-rules).

```python
from audiometa import validate_metadata_for_update, UnifiedMetadataKey

# Valid metadata
validate_metadata_for_update({UnifiedMetadataKey.TITLE: "Song Title"})

# Valid: empty string is allowed (represents setting field to empty)
validate_metadata_for_update({UnifiedMetadataKey.TITLE: ""})

# Valid: None value is allowed (represents field removal)
validate_metadata_for_update({UnifiedMetadataKey.TITLE: None})

# Valid: empty list is allowed
validate_metadata_for_update({UnifiedMetadataKey.ARTISTS: []})

# Valid: list with None values is allowed (None values will be filtered during writing)
validate_metadata_for_update({UnifiedMetadataKey.ARTISTS: [None, None]})

# Valid: rating with normalization (see Rating Validation Rules for details)
validate_metadata_for_update({UnifiedMetadataKey.RATING: 50}, normalized_rating_max_value=100)

# Invalid: negative rating
validate_metadata_for_update({UnifiedMetadataKey.RATING: -1})
# Raises: InvalidRatingValueError

# Valid: release date
validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: "2024-01-01"})

# Invalid: invalid release date format
validate_metadata_for_update({UnifiedMetadataKey.RELEASE_DATE: "2024/01/01"})
# Raises: InvalidMetadataFieldFormatError
```

### Writing Metadata (API Reference)

For validation before writing, see [Pre-Update Validation (API Reference)](#pre-update-validation-api-reference).

#### Metadata Dictionary Structure

When writing, metadata should be provided as a dictionary with keys corresponding to unified metadata fields defined in `UnifiedMetadataKey`.

```python
metadata = {
    UnifiedMetadataKey.TITLE: 'Song Title',
    UnifiedMetadataKey.ARTISTS: ['Artist 1', 'Artist 2'],
    UnifiedMetadataKey.ALBUM: 'Album Name',
    UnifiedMetadataKey.YEAR: 2024,
    UnifiedMetadataKey.GENRES_NAMES: ['Rock'],
    UnifiedMetadataKey.RATING: 85,
    UnifiedMetadataKey.BPM: 120,
    UnifiedMetadataKey.COMMENT: 'Some comments here',
}
```

**`update_metadata(file_path, metadata, **options)`\*\*

Updates metadata in a file. The function automatically calls pre-update validation on the metadata before writing (see [Pre-Update Validation](#pre-update-validation) for validation rules).

**Note:** `file_path` can be a string or `pathlib.Path` object.

```python
from audiometa import update_metadata

# Basic writing (recommended: use UnifiedMetadataKey constants)
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey

update_metadata("song.mp3", {
    UnifiedMetadataKey.TITLE: 'New Title',
    UnifiedMetadataKey.ARTISTS: ['Artist Name'],
    UnifiedMetadataKey.RATING: 85
})

# Format-specific writing
from audiometa.utils.MetadataFormat import MetadataFormat
update_metadata("song.wav", metadata, metadata_format=MetadataFormat.RIFF)

# Advanced examples

# Write to a specific ID3v2 version (e.g., ID3v2.4)
from audiometa.utils.MetadataFormat import MetadataFormat
update_metadata(
    "song.mp3",
    metadata,
    metadata_format=MetadataFormat.ID3V2,
    id3v2_version=(2, 4, 0)
)

# Write to ID3v2.3 (default)
update_metadata(
    "song.mp3",
    metadata,
    metadata_format=MetadataFormat.ID3V2
)

# Use writing strategy and specify ID3v2 version
from audiometa.utils.MetadataWritingStrategy import MetadataWritingStrategy
update_metadata(
    "song.mp3",
    metadata,
    metadata_strategy=MetadataWritingStrategy.SYNC,
    id3v2_version=(2, 4, 0)
)

"""
Note: The `id3v2_version` parameter lets you choose which ID3v2 version to target (e.g., (2, 3, 0) for ID3v2.3, (2, 4, 0) for ID3v2.4). This affects how multi-value fields and certain metadata are written.
"""
# Strategy-based writing
from audiometa.utils.MetadataWritingStrategy import MetadataWritingStrategy
update_metadata("song.mp3", metadata, metadata_strategy=MetadataWritingStrategy.CLEANUP)
```

##### Writing Defaults by Audio Format

The library automatically selects appropriate default metadata formats for different audio file types:

#### MP3 Files (ID3v2)

- **Default Format**: ID3v2.4
- **Why ID3v2.4?**: Most compatible with modern software and supports Unicode
- **Fallback**: If ID3v2.4 writing fails, automatically falls back to ID3v2.3

#### FLAC Files (Vorbis Comments)

- **Default Format**: Vorbis Comments
- **Why Vorbis?**: Native format for FLAC files, full Unicode support

#### WAV Files (RIFF INFO)

- **Default Format**: RIFF INFO chunks
- **Why RIFF?**: Native format for WAV files, widely supported

#### ID3v2 Version Selection

When writing to MP3 files, the library intelligently selects the best ID3v2 version:

```python
from audiometa import update_metadata

# The library automatically chooses ID3v2.3 for MP3 files for best compatibility
update_metadata("song.mp3", {"title": "Song Title"})

# You can override the version if needed
from audiometa.utils.MetadataFormat import MetadataFormat
update_metadata("song.mp3", {"title": "Song Title"},
                    metadata_format=MetadataFormat.ID3V2_4)  # Force ID3v2.4
```

#### Writing Strategies

The library provides flexible control over how metadata is written to files that may already contain metadata in other formats.

##### Available Strategies

1. **`SYNC` (Default)**: Write to native format and synchronize other metadata formats that are already present
2. **`PRESERVE`**: Write to native format only, preserve existing metadata in other formats
3. **`CLEANUP`**: Write to native format and remove all non-native metadata formats

##### Usage Examples

```python
from audiometa import update_metadata
from audiometa.utils.MetadataWritingStrategy import MetadataWritingStrategy

# SYNC strategy (default) - synchronize all existing formats
update_metadata("song.wav", {"title": "New Title"},
                    metadata_strategy=MetadataWritingStrategy.SYNC)

# CLEANUP strategy - remove non-native formats
update_metadata("song.wav", {"title": "New Title"},
                    metadata_strategy=MetadataWritingStrategy.CLEANUP)

# PRESERVE strategy - keep other formats unchanged
update_metadata("song.wav", {"title": "New Title"},
                    metadata_strategy=MetadataWritingStrategy.PRESERVE)
```

##### Default Behavior

By default, the library uses the **SYNC strategy** which writes metadata to the native format and synchronizes other metadata formats that are already present. This provides the best user experience by writing metadata where possible and handling unsupported fields gracefully.

- **MP3 files**: Writes to ID3v2 and syncs other formats
- **FLAC files**: Writes to Vorbis comments and syncs other formats
- **WAV files**: Writes to RIFF and syncs other formats

#### Forced Format Behavior

When you specify a `metadata_format` parameter, you **cannot** also specify a `metadata_strategy`:

- **Write only to the specified format**: Other formats are left completely untouched
- **Fail fast on unsupported fields**: Raises `MetadataFieldNotSupportedByMetadataFormatError` for any unsupported metadata
- **Predictable behavior**: No side effects on other metadata formats

```python
# Correct usage - specify only the format
update_metadata("song.mp3", metadata,
                    metadata_format=MetadataFormat.RIFF)  # Writes only to RIFF, ignores ID3v2

# This will raise MetadataWritingConflictParametersError - cannot specify both parameters
update_metadata("song.mp3", metadata,
                    metadata_format=MetadataFormat.RIFF,
                    metadata_strategy=MetadataWritingStrategy.CLEANUP)  # Raises MetadataWritingConflictParametersError
```

#### Usage Examples

**Default Behavior (SYNC strategy)**

```python
from audiometa import update_metadata

# WAV file with existing ID3v1 tags (30-char limit)
update_metadata("song.wav", {"title": "This is a Very Long Title That Exceeds ID3v1 Limits"})

# Result:
# - RIFF tags: Updated with full title (native format)
# - ID3v1 tags: Synchronized with truncated title (30 chars max)
# - When reading: RIFF title is returned (higher precedence)
# Note: ID3v1 title becomes "This is a Very Long Title Th" (truncated)
```

**CLEANUP Strategy - Remove Non-Native Formats**

```python
from audiometa import update_metadata
from audiometa.utils.MetadataWritingStrategy import MetadataWritingStrategy

# Clean up WAV file - remove ID3v2, keep only RIFF
update_metadata("song.wav", {"title": "New Title"},
                    metadata_strategy=MetadataWritingStrategy.CLEANUP)

# Result:
# - ID3v2 tags: Removed completely
# - RIFF tags: Updated with new metadata
# - When reading: Only RIFF metadata available
```

**SYNC Strategy - Synchronize All Existing Formats**

```python
# Synchronize all existing metadata formats with same values
update_metadata("song.wav", {"title": "New Title"},
                    metadata_strategy=MetadataWritingStrategy.SYNC)

# Result:
# - RIFF tags: Synchronized with new metadata (native format)
# - ID3v2 tags: Synchronized with new metadata (if present)
# - ID3v1 tags: Synchronized with new metadata (if present)
# - When reading: RIFF title is returned (highest precedence)
# Note: SYNC preserves and updates ALL existing metadata formats
```

**Format-Specific Writing**

```python
from audiometa.utils.MetadataFormat import MetadataFormat

# Write specifically to ID3v2 format (even for WAV files)
update_metadata("song.wav", {"title": "New Title"},
                    metadata_format=MetadataFormat.ID3V2)

# Write specifically to RIFF format
update_metadata("song.wav", {"title": "New Title"},
                    metadata_format=MetadataFormat.RIFF)
```

### Deleting Metadata (API Reference)

#### Delete All Metadata From All Formats

Deletes all metadata from all supported formats for the file type.

**`delete_all_metadata(file_path, metadata_format=None)`**

**Note:** `file_path` can be a string or `pathlib.Path` object.

```python
from audiometa import delete_all_metadata

# Delete all metadata from all supported formats for the file type
delete_all_metadata("song.mp3")
```

#### Delete All Metadata From A Specific Format

Deletes all metadata from a specific format.

**`delete_all_metadata(file_path, metadata_format=MetadataFormat.ID3V2)`**

**Note:** `file_path` can be a string or `pathlib.Path` object.

```python
from audiometa import delete_all_metadata

# Delete all metadata from a specific format
delete_all_metadata("song.mp3", metadata_format=MetadataFormat.ID3V2)
```

When specifying a metadata format not supported by the audio format of the file, raises a MetadataFormatNotSupportedByAudioFormatError.

```python
from audiometa import delete_all_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.exceptions import MetadataFormatNotSupportedByAudioFormatError

try:
    delete_all_metadata("path/to/your/audio.mp3", metadata_format=MetadataFormat.RIFF)
except MetadataFormatNotSupportedByAudioFormatError as e:
    print(f"Error: {e}")
```

The library provides specific exception types for different error conditions:

```python
from audiometa.exceptions import (
    FileCorruptedError,
    FileTypeNotSupportedError,
    MetadataFieldNotSupportedByMetadataFormatError,
    InvalidMetadataFieldTypeError,
    InvalidMetadataFieldFormatError,
    AudioFileMetadataParseError
)

try:
    metadata = get_unified_metadata("invalid_file.txt")
except FileTypeNotSupportedError:
    print("File format not supported")
except FileCorruptedError:
    print("File is corrupted")
except MetadataFieldNotSupportedByMetadataFormatError:
    print("Metadata field not supported for this format")
except InvalidMetadataFieldTypeError:
    print("Invalid metadata field type")
except InvalidMetadataFieldFormatError:
    print("Invalid metadata field format (e.g., date format)")
except AudioFileMetadataParseError:
    print("Failed to parse audio file metadata")
```

### Error Handling (API Reference)

The library provides comprehensive exception handling for all operations. All library functions can raise specific exception types that help you handle errors appropriately.

**For comprehensive exception documentation**, including detailed explanations, common causes, and examples for all exceptions, see the dedicated guide:

**[Error Handling Guide: Exceptions and Error Management](docs/ERROR_HANDLING_GUIDE.md)**

#### Quick Reference: Common Exceptions

The library defines custom exceptions organized into categories:

**File-Related Exceptions:**

- `FileCorruptedError` - Base exception for file corruption errors
- `FlacMd5CheckFailedError` - FLAC MD5 checksum verification failed
- `FileByteMismatchError` - File bytes don't match expected content
- `InvalidChunkDecodeError` - Chunk cannot be decoded
- `DurationNotFoundError` - Audio duration cannot be determined
- `AudioFileMetadataParseError` - Metadata parsing from external tools failed
- `FileTypeNotSupportedError` - File type not supported (only `.mp3`, `.flac`, `.wav`)

**Metadata Format Exceptions:**

- `MetadataFormatNotSupportedByAudioFormatError` - Format not supported for audio type
- `MetadataFieldNotSupportedByMetadataFormatError` - Field not supported by format
- `MetadataFieldNotSupportedByLibError` - Field not supported by library
- `MetadataWritingConflictParametersError` - Conflicting parameters specified

**Validation Exceptions:**

- `InvalidMetadataFieldTypeError` - Invalid field type (e.g., string instead of list)
- `InvalidMetadataFieldFormatError` - Invalid field format (e.g., date format)
- `InvalidRatingValueError` - Invalid rating value

**Configuration Exceptions:**

- `ConfigurationError` - Configuration error in metadata manager

**Standard Python Exceptions:**

- `FileNotFoundError` - File does not exist
- `IOError`, `OSError`, `PermissionError` - System-level I/O errors

#### Basic Exception Handling Example

```python
from audiometa import get_unified_metadata, update_metadata
from audiometa.exceptions import (
    FileTypeNotSupportedError,
    FileCorruptedError,
    MetadataFieldNotSupportedByMetadataFormatError,
    InvalidMetadataFieldTypeError,
)

try:
    metadata = get_unified_metadata("song.mp3")
except FileTypeNotSupportedError:
    print("File format not supported")
except FileCorruptedError:
    print("File is corrupted")
except FileNotFoundError:
    print("File not found")

try:
    update_metadata("song.mp3", {"title": "New Title"})
except InvalidMetadataFieldTypeError:
    print("Invalid metadata field type")
except MetadataFieldNotSupportedByMetadataFormatError:
    print("Field not supported for this format")
except PermissionError:
    print("Permission denied")
```

#### Exception Handling for Mutagen Operations

The library uses mutagen internally and wraps all mutagen operations with proper exception handling. Mutagen-specific exceptions are converted to `FileCorruptedError` with descriptive messages, while standard I/O exceptions (`IOError`, `OSError`, `PermissionError`) are re-raised as-is.

See the **[Error Handling Guide](docs/ERROR_HANDLING_GUIDE.md)** for detailed information about mutagen exception handling and all exception types.

## Metadata Guide

### Metadata Field Guide: Support and Handling

For a comprehensive reference on metadata field support and handling across all audio formats (ID3v1, ID3v2, Vorbis, RIFF), including multiple values, genres, ratings, track numbers, release dates, and lyrics support, see the dedicated guide:

**[Metadata Field Guide: Support and Handling](docs/METADATA_FIELD_GUIDE.md)**

### Audio Technical Info Guide

For information about audio information (duration, bitrate, sample rate, channels, file size, format info, MD5 checksum validation and repair), see the dedicated guide:

**[Audio Technical Info Guide](docs/AUDIO_TECHNICAL_INFO_GUIDE.md)**

### Error Handling Guide

For comprehensive documentation on all exceptions that can be raised by the library, including detailed explanations, common causes, usage examples, and mutagen exception handling, see the dedicated guide:

**[Error Handling Guide: Exceptions and Error Management](docs/ERROR_HANDLING_GUIDE.md)**

### Unsupported Metadata Handling

The library handles unsupported metadata consistently across all strategies:

- **Forced format** (when `metadata_format` is specified): Always fails fast by raising `MetadataFieldNotSupportedByMetadataFormatError` for any unsupported field. **No writing is performed** - the file remains completely unchanged.
- **All strategies (SYNC, PRESERVE, CLEANUP) with `fail_on_unsupported_field=False` (default)**: Handle unsupported fields gracefully by logging warnings and continuing with supported fields
- **All strategies (SYNC, PRESERVE, CLEANUP) with `fail_on_unsupported_field=True`**: Fails fast if any field is not supported by the target format. **No writing is performed** - the file remains completely unchanged (atomic operation).

#### Format-Specific Limitations

| Format         | Forced Format                     | All Strategies with `fail_on_unsupported_field=False`       | All Strategies with `fail_on_unsupported_field=True` |
| -------------- | --------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------- |
| **RIFF (WAV)** | Always fails fast, **no writing** | Logs warnings for unsupported fields, writes supported ones | Fails fast for unsupported fields, **no writing**    |
| **ID3v1**      | Always fails fast, **no writing** | Logs warnings for unsupported fields, writes supported ones | Fails fast for unsupported fields, **no writing**    |
| **ID3v2**      | Always fails fast, **no writing** | All fields supported                                        | All fields supported                                 |
| **Vorbis**     | Always fails fast, **no writing** | All fields supported                                        | All fields supported                                 |

#### Atomic Write Operations

When `fail_on_unsupported_field=True` is used, the library ensures **atomic write operations**:

- **All-or-nothing behavior**: Either all metadata is written successfully, or nothing is written at all
- **File integrity**: If any field is unsupported, the file remains completely unchanged
- **No partial updates**: Prevents inconsistent metadata states where only some fields are updated
- **Error safety**: Ensures that failed operations don't leave files in a partially modified state

#### Example: Handling Unsupported Metadata

```python
from audiometa import update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.MetadataWritingStrategy import MetadataWritingStrategy

# All strategies - handle unsupported fields gracefully with warnings
update_metadata("song.wav", {"title": "Song", "rating": 85, "bpm": 120})
# Result: Writes title and rating to RIFF, logs warning about BPM, continues

update_metadata("song.wav", {"title": "Song", "rating": 85, "bpm": 120},
                    metadata_strategy=MetadataWritingStrategy.PRESERVE)
# Result: Writes title and rating to RIFF, logs warning about BPM, preserves other formats

update_metadata("song.wav", {"title": "Song", "rating": 85, "bpm": 120},
                    metadata_strategy=MetadataWritingStrategy.CLEANUP)
# Result: Writes title and rating to RIFF, logs warning about BPM, removes other formats

# Forced format - always fails fast for unsupported fields, no writing performed
try:
    update_metadata("song.wav", {"title": "Song", "rating": 85, "bpm": 120},
                        metadata_format=MetadataFormat.RIFF)
except MetadataFieldNotSupportedByMetadataFormatError as e:
    print(f"BPM not supported in RIFF format: {e}")
    # File remains completely unchanged - no metadata was written

# Strategies with fail_on_unsupported_field=True - atomic operation, no writing on failure
try:
    update_metadata("song.wav", {"title": "Song", "rating": 85, "bpm": 120},
                        metadata_strategy=MetadataWritingStrategy.SYNC,
                        fail_on_unsupported_field=True)
except MetadataFieldNotSupportedByMetadataFormatError as e:
    print(f"BPM not supported: {e}")
    # File remains completely unchanged - no metadata was written (atomic operation)

# Practical example: Demonstrating atomic behavior
from audiometa import get_unified_metadata

# File with existing metadata
original_metadata = get_unified_metadata("song.wav")
print(f"Original title: {original_metadata.get('title')}")  # e.g., "Original Title"

# Attempt to write metadata with unsupported field
try:
    update_metadata("song.wav", {
        "title": "New Title",      # This would be supported
        "rating": 85,              # This would be supported
        "bpm": 120                 # This is NOT supported by RIFF format
    }, fail_on_unsupported_field=True)
except MetadataFieldNotSupportedByMetadataFormatError:
    pass

# Verify file is unchanged (atomic behavior)
final_metadata = get_unified_metadata("song.wav")
print(f"Final title: {final_metadata.get('title')}")  # Still "Original Title" - no changes made
```

## Command Line Interface

AudioMeta provides a powerful command-line interface for quick metadata operations without writing Python code.

### Installation {#cli-installation}

After installing the package, the `audiometa` command will be available:

```bash
pip install audiometa-python
audiometa --help
```

### Basic Usage

#### Reading Metadata {#cli-reading-metadata}

```bash
# Read full metadata from a file
audiometa read song.mp3

# Read unified metadata only (simplified output)
audiometa unified song.mp3

# Read multiple files
audiometa read *.mp3

# Process directory recursively
audiometa read music/ --recursive

# Output in different formats
audiometa read song.mp3 --format table
audiometa read song.mp3 --format yaml
audiometa read song.mp3 --output metadata.json
```

#### Writing Metadata {#cli-writing-metadata}

```bash
# Write basic metadata
audiometa write song.mp3 --title "New Title" --artist "Artist Name"

# Write multiple fields
audiometa write song.mp3 --title "Song Title" --artist "Artist" --album "Album" --year "2024" --rating 85

# Update multiple files
audiometa write *.mp3 --artist "New Artist"
```

#### Deleting Metadata {#cli-deleting-metadata}

```bash
# Delete all metadata from a file
audiometa delete song.mp3

# Delete metadata from multiple files
audiometa delete *.mp3
```

### Advanced Options

#### Output Control

```bash
# Exclude technical information
audiometa read song.mp3 --no-technical

# Exclude header information
audiometa read song.mp3 --no-headers

# Save to file
audiometa read song.mp3 --output metadata.json
```

#### Error Handling {#cli-error-handling}

```bash
# Continue processing other files on error
audiometa read *.mp3 --continue-on-error
```

#### Batch Processing

```bash
# Process all audio files in a directory
audiometa read music/ --recursive

# Process specific file patterns
audiometa read "**/*.mp3" --recursive
```

### Output Formats

- **JSON** (default): Structured data for programmatic use
- **YAML**: Human-readable structured format (requires PyYAML)
- **Table**: Simple text table format

### Examples

```bash
# Quick metadata check
audiometa unified song.mp3 --format table

# Batch metadata update
audiometa write music/ --recursive --artist "Various Artists"

# Export metadata for analysis
audiometa read music/ --recursive --format json --output all_metadata.json

# Clean up metadata
audiometa delete music/ --recursive
```

## Requirements

- Python 3.12+
- mutagen==1.45.0
- ffprobe (for WAV file processing)
- flac (for FLAC MD5 validation)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to this project.

When submitting issues or pull requests, please use the provided templates:

- **Bug Reports**: Use the bug report template when opening an issue
- **Feature Requests**: Use the feature request template for new ideas
- **Pull Requests**: The PR template will guide you through the submission process

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

The Apache 2.0 license provides patent protection, which helps prevent contributors and users from facing patent litigation from other contributors. This makes it a safer choice for both individual contributors and organizations compared to licenses without explicit patent grants.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes.
