# AudioMeta Python

[![CI](https://github.com/Andreas-Garcia/audiometa/actions/workflows/ci.yml/badge.svg)](https://github.com/Andreas-Garcia/audiometa/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange)](https://github.com/Andreas-Garcia/audiometa)

A powerful, unified Python library for reading and writing audio metadata across multiple formats. AudioMeta supports MP3, FLAC, and WAV audio files, working seamlessly with ID3v1, ID3v2, Vorbis, and RIFF metadata formats through a single, consistent API.

**Author**: [Andreas Garcia](https://github.com/Andreas-Garcia)

## Table of Contents

- [Features](#features)
- [Supported Formats](#supported-formats)
  - [Supported Audio Formats Per Metadata Format](#supported-audio-formats-per-metadata-format)
  - [Supported Metadata Formats per Audio Format](#supported-metadata-formats-per-audio-format)
  - [Format Capabilities](#format-capabilities)
    - [ID3v1 Metadata Format](#id3v1-metadata-format)
    - [ID3v2 Metadata Format](#id3v2-metadata-format)
    - [Vorbis Metadata Format](#vorbis-metadata-format)
    - [RIFF Metadata Format](#riff-metadata-format)
- [Installation](#installation)
  - [System Requirements](#system-requirements)
  - [Installing Required Tools](#installing-required-tools)
    - [ffprobe (for WAV file processing)](#ffprobe-for-wav-file-processing)
    - [flac (for FLAC MD5 validation)](#flac-for-flac-md5-validation)
  - [Verifying Installation](#verifying-installation)
  - [External Tools Usage](#external-tools-usage)
- [Getting Started](#getting-started)
  - [What You Need](#what-you-need)
  - [Your First Steps](#your-first-steps)
  - [Common Use Cases](#common-use-cases)
- [Quick Start](#quick-start)
  - [Reading Metadata](#reading-metadata)
    - [Reading from a specific metadata format](#reading-from-a-specific-metadata-format)
    - [Reading All Metadata](#reading-all-metadata)
    - [Reading Specific Metadata Fields (Quick Start)](#reading-specific-metadata-fields-quick-start)
    - [Reading Full Metadata From All Formats Including Headers and Technical Info](#reading-full-metadata-from-all-formats-including-headers-and-technical-info)
  - [Writing Metadata](#writing-metadata)
  - [Deleting Metadata](#deleting-metadata)
    - [Delete All Metadata (Complete Removal)](#delete-all-metadata-complete-removal)
    - [Remove Specific Fields (Selective Removal)](#remove-specific-fields-selective-removal)
    - [Comparison Table](#comparison-table)
    - [Example Scenarios](#example-scenarios)
- [Core API Reference](#core-api-reference)
  - [Reading Metadata (API Reference)](#reading-metadata-api-reference)
    - [Reading Priorities (Tag Precedence)](#reading-priorities-tag-precedence)
      - [FLAC Files Reading Priorities](#flac-files-reading-priorities)
      - [MP3 Files Reading Priorities](#mp3-files-reading-priorities)
      - [WAV Files Reading Priorities](#wav-files-reading-priorities)
    - [Reading All Metadata From All Metadata Formats Including Priority Logic](#reading-all-metadata-from-all-metadata-formats-including-priority-logic)
    - [Reading All Metadata From A Specific Format](#reading-all-metadata-from-a-specific-format)
    - [Reading All Metadata From A ID3v2 Format With Version](#reading-all-metadata-from-a-id3v2-format-with-version)
    - [Reading Specific Metadata Fields](#reading-specific-metadata-fields)
    - [Reading Full Metadata From All Formats Including Headers and Technical Info](#reading-full-metadata-from-all-formats-including-headers-and-technical-info-1)
  - [Writing Metadata (API Reference)](#writing-metadata-api-reference)
    - [Metadata Dictionary Structure](#metadata-dictionary-structure)
    - [Validation](#validation)
    - [Writing Defaults by Audio Format](#writing-defaults-by-audio-format)
    - [Writing Strategies](#writing-strategies)
      - [Available Strategies](#available-strategies)
      - [Usage Examples](#usage-examples)
      - [Default Behavior](#default-behavior)
      - [Forced Format Behavior](#forced-format-behavior)
  - [Deleting Metadata (API Reference)](#deleting-metadata-api-reference)
    - [Delete All Metadata From All Formats](#delete-all-metadata-from-all-formats)
    - [Delete All Metadata From A Specific Format](#delete-all-metadata-from-a-specific-format)
- [Error Handling](#error-handling)
- [Metadata Field Guide: Support and Handling](#metadata-field-guide-support-and-handling)
  - [Metadata Support by Format](#metadata-support-by-format)
    - [ID3v2](#id3v2-1)
    - [ID3v1](#id3v1-1)
    - [Vorbis](#vorbis-1)
    - [RIFF](#riff-1)
    - [Edge Case Handling](#edge-case-handling)
  - [Multiple Values](#multiple-values)
    - [Semantic Classification](#semantic-classification)
    - [Semantically Single-Value Fields](#semantically-single-value-fields)
    - [Semantically Multi-Value Fields](#semantically-multi-value-fields)
      - [List of Semantically Multi-Value Fields](#list-of-semantically-multi-value-fields)
      - [Ways to handle multiple values](#ways-to-handle-multiple-values)
        - [Multiple Field Instances (Multi-Frame/Multi-Key)](#multiple-field-instances-multi-frame-multi-key)
        - [Single field with separated values (separator-based)](#single-field-with-separated-values-separator-based)
      - [Reading Semantically Multiple Values](#reading-semantically-multiple-values)
        - [Smart separator parsing of concatenated values](#smart-separator-parsing-of-concatenated-values)
        - [Detailed Examples of Smart Semantically Multi-Value Logic](#detailed-examples-of-smart-semantically-multi-value-logic)
      - [Writing Semantically Multiple Values](#writing-semantically-multiple-values)
        - [Strategy Overview](#strategy-overview)
        - [Automatic Empty Value Filtering](#automatic-empty-value-filtering)
        - [Smart Separator Selection](#smart-separator-selection)
        - [Examples of Smart Separator Selection](#examples-of-smart-separator-selection)
  - [Genre Handling](#genre-handling)
    - [Genre Support by Format](#genre-support-by-format)
      - [Genre Support Matrix](#genre-support-matrix)
      - [ID3v1 Genre Support](#id3v1-genre-support)
      - [ID3v2.3 Genre Support](#id3v2.3-genre-support)
      - [ID3v2.4 Genre Support](#id3v2.4-genre-support)
      - [Vorbis Genre Support](#vorbis-genre-support)
      - [RIFF Genre Support](#riff-genre-support)
    - [ID3v1 Genre Code System](#id3v1-genre-code-system)
    - [Reading and Writing Strategy](#reading-and-writing-strategy)
      - [Reading Genres](#reading-genres)
      - [Writing Genres](#writing-genres)
        - [Writing Genres for ID3v1](#writing-genres-for-id3v1)
        - [Writing Genres for ID3v2.3](#writing-genres-for-id3v2.3)
        - [Writing Genres for ID3v2.4](#writing-genres-for-id3v2.4)
        - [Writing Genres for Vorbis](#writing-genres-for-vorbis)
        - [Writing Genres for RIFF](#writing-genres-for-riff)
  - [Rating Handling](#rating-handling)
    - [The Rating Profile Problem](#the-rating-profile-problem)
    - [Rating Profile Types](#rating-profile-types)
    - [Rating Normalization](#rating-normalization)
    - [Normalized Rating Scale](#normalized-rating-scale)
    - [How AudioMeta Handles Rating Profiles](#how-audiometa-handles-rating-profiles)
      - [Reading Ratings](#reading-ratings)
      - [Writing Ratings](#writing-ratings)
        - [Rating Writing Profiles](#rating-writing-profiles)
        - [Rating Validation Rules](#rating-validation-rules)
    - [Half-Star Rating Support](#half-star-rating-support)
  - [Track Number](#track-number)
    - [ID3v1 Track Number Format](#id3v1-track-number-format)
    - [ID3v2 Track Number Format](#id3v2-track-number-format)
    - [Vorbis Track Number Format](#vorbis-track-number-format)
    - [RIFF Track Number Format](#riff-track-number-format)
    - [Reading And Writing Track Number](#reading-and-writing-track-number)
      - [Reading Track Number](#reading-track-number)
      - [Writing Track Number](#writing-track-number)
  - [Lyrics Support](#lyrics-support)
    - [Synchronized Lyrics](#synchronized-lyrics)
    - [Unsynchronized Lyrics](#unsynchronized-lyrics)
      - [ID3v1 Unsynchronized Lyrics](#id3v1-unsynchronized-lyrics)
      - [ID3v2 Unsynchronized Lyrics](#id3v2-unsynchronized-lyrics)
      - [RIFF Unsynchronized Lyrics](#riff-unsynchronized-lyrics)
      - [Vorbis Unsynchronized Lyrics](#vorbis-unsynchronized-lyrics)
  - [Unsupported Metadata Handling](#unsupported-metadata-handling)
    - [Format-Specific Limitations](#format-specific-limitations-unsupported)
    - [Atomic Write Operations](#atomic-write-operations)
    - [Example: Handling Unsupported Metadata](#example-handling-unsupported-metadata)
  - [None vs Empty String Handling](#none-vs-empty-string-handling)
    - [Example](#example)
- [Command Line Interface](#command-line-interface)
  - [Installation](#cli-installation)
  - [Basic Usage](#basic-usage)
    - [Reading Metadata](#cli-reading-metadata)
    - [Writing Metadata](#cli-writing-metadata)
    - [Deleting Metadata](#cli-deleting-metadata)
  - [Advanced Options](#advanced-options)
    - [Output Control](#output-control)
    - [Error Handling](#cli-error-handling)
    - [Batch Processing](#batch-processing)
  - [Output Formats](#output-formats)
  - [Examples](#examples)
- [Requirements](#requirements)
- [Changelog](#changelog)
- [Contributing](CONTRIBUTING.md)
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

The library requires two external tools for full functionality:

#### ffprobe (for WAV file processing)

**macOS:**

```bash
# Using Homebrew
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**CentOS/RHEL/Fedora:**

```bash
# CentOS/RHEL
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

**Windows:**

- Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Add to your system PATH

#### flac (for FLAC MD5 validation)

**macOS:**

```bash
# Using Homebrew
brew install flac

# Using MacPorts
sudo port install flac
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install flac
```

**CentOS/RHEL/Fedora:**

```bash
# CentOS/RHEL
sudo yum install flac

# Fedora
sudo dnf install flac
```

**Windows:**

- Download from [https://xiph.org/flac/download.html](https://xiph.org/flac/download.html)
- Add to your system PATH

#### Verifying Installation

After installation, verify the tools are available:

```bash
ffprobe -version
flac --version
```

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

**Note:** `file_path` can be a string, `pathlib.Path` object, or `_AudioFile` instance.

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

**Note:** `file_path` can be a string, `pathlib.Path` object, or `_AudioFile` instance.

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

**Note:** `file_path` can be a string, `pathlib.Path` object, or `_AudioFile` instance.

```python
from audiometa import get_full_metadata

full_metadata = get_full_metadata("song.mp3")
```

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

**Note:** `file_path` can be a string, `pathlib.Path` object, or `_AudioFile` instance.

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

**Note:** `file_path` can be a string, `pathlib.Path` object, or `_AudioFile` instance.

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

**Note:** `file_path` can be a string, `pathlib.Path` object, or `_AudioFile` instance.

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

- `file_path`: Path to the audio file (str, Path, or \_AudioFile)
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

### Writing Metadata (API Reference)

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

#### Validation

The library validates metadata value types and formats passed to `update_metadata` when keys are provided as `UnifiedMetadataKey` instances. Rules:

- `None` values are allowed and indicate field removal.
- For fields whose expected type is `list[...]` (for example `ARTISTS` or `GENRES_NAMES`) the validator accepts only lists. Each list element is checked against the expected inner type (e.g., `str` for `ARTISTS`).
- For plain types (`str`, `int`, etc.) the value must be an instance of that type.
- On type mismatch the library raises `InvalidMetadataFieldTypeError`.
- **Date Format Validation**: The `RELEASE_DATE` field accepts two formats:
  - `YYYY` (4 digits) - for year-only dates (e.g., `"2024"`)
  - `YYYY-MM-DD` (ISO-like format) - for full dates (e.g., `"2024-01-01"`)
  - Invalid formats raise `InvalidMetadataFieldFormatError` (e.g., `"2024/01/01"`, `"2024-1-1"`, `"not-a-date"`)

Note: the validator currently uses the `UnifiedMetadataKey` enum to determine expected types. Calls that use plain string keys (the older examples in this README) are accepted by the API but are not validated by this mechanism unless you pass `UnifiedMetadataKey` instances. You can continue using string keys, or prefer `UnifiedMetadataKey` for explicit validation and IDE-friendly code.

\*\*`update_metadata(file_path, metadata, **options)`\*\*

Updates metadata in a file.

**Note:** `file_path` can be a string, `pathlib.Path` object, or `_AudioFile` instance.

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

**Note:** `file_path` can be a string, `pathlib.Path` object, or `_AudioFile` instance.

```python
from audiometa import delete_all_metadata

# Delete all metadata from all supported formats for the file type
delete_all_metadata("song.mp3")
```

#### Delete All Metadata From A Specific Format

Deletes all metadata from a specific format.

**`delete_all_metadata(file_path, metadata_format=MetadataFormat.ID3V2)`**

**Note:** `file_path` can be a string, `pathlib.Path` object, or `_AudioFile` instance.

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

## Metadata Field Guide: Support and Handling

This section covers AudioMeta's metadata field support across audio formats (ID3v1, ID3v2, Vorbis, RIFF), including support matrices, multiple value handling, format limitations, and special cases for genres, ratings, and edge cases.

### Metadata Support by Format

The library supports a comprehensive set of metadata fields across different audio formats. The table below shows which fields are supported by each format:

| Field               | ID3v1             | ID3v2                      | Vorbis                         | RIFF            | AudioMeta Support     |
| ------------------- | ----------------- | -------------------------- | ------------------------------ | --------------- | --------------------- |
| Text Encoding       | ASCII             | UTF-16/ISO (v2.3)          | UTF-8                          | ASCII/UTF-8     | UTF-8                 |
|                     |                   | + UTF-8 (v2.4)             |                                |                 |                       |
| Max Text Length     | 30 chars          | ~8M chars                  | ~8M chars                      | ~1M chars       | Format limit          |
| Date Time Formats   | YYYY              | YYYY+DDMM (v2.3)           | YYYY-MM-DD                     | YYYY-MM-DD      | ISO 8601              |
|                     |                   | YYYY-MM-DD (v2.4)          |                                |                 |                       |
| Technical Info      |                   |                            |                                |                 |                       |
| - Duration          | ✓                 | ✓                          | ✓                              | ✓               | ✓                     |
| - Bitrate           | ✓                 | ✓                          | ✓                              | ✓               | ✓                     |
| - Sample Rate       | ✓                 | ✓                          | ✓                              | ✓               | ✓                     |
| - Channels          | ✓ (1-2)           | ✓ (1-255)                  | ✓ (1-255)                      | ✓ (1-2)         | ✓                     |
| - File Size         | ✓                 | ✓                          | ✓                              | ✓               | ✓                     |
| - Format Info       | ✓                 | ✓                          | ✓                              | ✓               | ✓                     |
| - MD5 Checksum      |                   |                            | ✓                              |                 | ✓ (Flac)              |
| Title               | TITLE (30)        | TIT2                       | TITLE                          | INAM            | TITLE                 |
| Artists             | ARTIST (30)       | TPE1                       | ARTIST                         | IART            | ARTISTS (list)        |
| Album               | ALBUM (30)        | TALB                       | ALBUM                          | IPRD            | ALBUM                 |
| Album Artists       | ✗                 | TPE2                       | ALBUMARTIST                    | IAAR\*          | ALBUM_ARTISTS (list)  |
| Genres              | GENRE (1#)        | TCON                       | GENRE                          | IGNR            | GENRES_NAMES (list)   |
| Release Date        | YEAR (4)          | TYER (4) + TDAT (4) (v2.3) | DATE (10)                      | ICRD (10)       | RELEASE_DATE          |
|                     |                   | TDRC (10) (v2.4)           |                                |                 |                       |
| Track Number        | TRACK (1#) (v1.1) | TRCK (0-255#)              | TRACKNUMBER (Unlim#)           | IPRT\* (Unlim#) | TRACK_NUMBER          |
| Disc Number         | ✗                 | TPOS (0-255#)              | DISCNUMBER (Unlim#)            | ✗               |                       |
| Rating              | ✗                 | POPM (0-255#)              | RATING (0-100#)                | IRTD\* (0-100#) | RATING                |
| BPM                 | ✗                 | TBPM (0-65535#)            | BPM (0-65535#)                 | IBPM\*          | BPM                   |
| Language            | ✗                 | TLAN (3)                   | LANGUAGE (3)                   | ILNG\* (3)      | LANGUAGE              |
| Composers           | ✗                 | TCOM                       | COMPOSER                       | ICMP            | COMPOSERS (list)      |
| Publisher           | ✗                 | TPUB                       | ORGANIZATION                   | ✗               | PUBLISHER             |
| Copyright           | ✗                 | TCOP                       | COPYRIGHT                      | ICOP            | COPYRIGHT             |
| Lyrics              | ✗                 | USLT                       | LYRICS\*                       | ✗               | UNSYNCHRONIZED_LYRICS |
| Synchronized Lyrics | ✗                 | SYLT                       | ✗                              | ✗               |                       |
| Comment             | COMMENT (28)      | COMM                       | COMMENT                        | ICMT            | COMMENT               |
| Encoder             | ✗                 | TENC                       | ENCODEDBY                      | ISFT            |                       |
| URL                 | ✗                 | WOAR                       | ✗                              | ✗               |                       |
| ISRC                | ✗                 | TSRC (12)                  | ISRC (12)                      | ✗               |                       |
| Mood                | ✗                 | TMOO                       | MOOD                           | ✗               |                       |
| Key                 | ✗                 | TKEY (3)                   | KEY (3)                        | ✗               |                       |
| Original Date       | ✗                 | TORY (10)                  | ORIGINALDATE (10)              | ✗               |                       |
| Remixer             | ✗                 | TPE4                       | REMIXER                        | ✗               |                       |
| Conductors          | ✗                 | TPE3                       | CONDUCTOR                      | ✗               |                       |
| Cover Art           | ✗                 | APIC (10MB#)               | METADATA_BLOCK_PICTURE (10MB#) | ✗               |                       |
| Compilation         | ✗                 | TCMP (1#)                  | COMPILATION (1#)               | ✗               |                       |
| Media Type          | ✗                 | TMED                       | MEDIA                          | ✗               |                       |
| File Owner          | ✗                 | TOWN                       | OWNER                          | ✗               |                       |
| Recording Date      | ✗                 | TDRC (10)                  | RECORDINGDATE (10)             | ✗               |                       |
| File Size           | ✗                 | TSIZ (16#)                 | FILESIZE                       | ✗               |                       |
| Encoder Settings    | ✗                 | TSSE                       | ENCODERSETTINGS                | ✗               |                       |
| ReplayGain          | ✗                 | TXXX (REPLAYGAIN)          | REPLAYGAIN                     | ✗               | REPLAYGAIN            |
| MusicBrainz ID      | ✗                 | TXXX (36)                  | MUSICBRAINZ\_\* (36)           | ✗               |                       |
| Arranger            | ✗                 | TPE2                       | ARRANGER                       | ✗               |                       |
| Version             | ✗                 | TIT3                       | VERSION                        | ✗               |                       |
| Performance         | ✗                 | TPE1                       | PERFORMER                      | ✗               |                       |
| Archival Location   | ✗                 | ✗                          | ✗                              | IARL\*          | ARCHIVAL_LOCATION     |
| Keywords            | ✗                 | ✗                          | ✗                              | IKEY\*          |                       |
| Subject             | ✗                 | ✗                          | ✗                              | ISBJ\*          |                       |
| Original Artist     | ✗                 | TOPE                       | ORIGINALARTIST                 | ✗               |                       |
| Set Subtitle        | ✗                 | TIT3                       | ALBUMARTIST                    | ✗               |                       |
| Initial Key         | ✗                 | TKEY (3)                   | KEY (3)                        | ✗               |                       |
| Involved People     | ✗                 | TIPL                       | INVOLVEDPEOPLE                 | ✗               |                       |
| Musicians           | ✗                 | TMCL                       | MUSICIAN                       | ✗               |                       |
| Part of Set         | ✗                 | TPOS                       | DISCNUMBER                     | ✗               |                       |

### Multiple Values

The library intelligently handles multiple values across different metadata formats, automatically choosing the best approach for each situation.

#### Semantic Classification

Fields are classified based on their intended use:

- **Semantically Multi-Value Fields**: Fields that can logically contain multiple values (e.g., `ARTISTS`, `GENRES_NAMES`). They can be stored as multiple entries or concatenated values.
- **Semantically Single-Value Fields**: Fields that are intended to hold a single value (e.g., `TITLE`, `ALBUM`). They are typically stored as a single entry but some formats may allow multiple entries.

#### Semantically Single-Value Fields

The library always returns only the first value for these fields, regardless of how many values are present in the metadata.

#### Semantically Multi-Value Fields

The library can handle multiple values for these fields.

##### List of Semantically Multi-Value Fields

The following fields are treated as semantically multi-value:

- `ARTISTS` - Multiple artist names for the track
- `ALBUM_ARTISTS` - Multiple album artist names
- `GENRES_NAMES` - Multiple genre classifications
- `COMPOSERS` - Multiple composer names
- `MUSICIANS` - Multiple musician credits
- `CONDUCTORS` - Multiple conductor names
- `ARRANGERS` - Multiple arranger names
- `LYRICISTS` - Multiple lyricist names
- `INVOLVED_PEOPLE` - Multiple involved people credits
- `PERFORMERS` - Multiple performer names

##### Ways to handle multiple values

Metadata formats can represent multi-value fields in two ways:

##### Multiple Field Instances (Multi-Frame/Multi-Key)

Each value is stored as a separate instance of the same field or frame.

```
ARTIST=Artist 1
ARTIST=Artist 2
ARTIST=Artist 3
```

- **Officially supported**: Vorbis Comments
- **Technically possible**: ID3v2.3, ID3v2.4, RIFF INFO
- **Not supported**: ID3v1

| Format  | Official Support | Technically possible | Notes                                                                           |
| ------- | ---------------- | -------------------- | ------------------------------------------------------------------------------- |
| ID3v1   | ❌ No            | ❌ No                | Only one field per tag; repeated fields not allowed                             |
| ID3v2.3 | ❌ No            | ✅ Yes               | Multiple frames allowed technically, but not officially defined for text values |
| ID3v2.4 | ❌ No            | ✅ Yes               | Uses single frames with null-separated values for multi-value text fields       |
| RIFF    | ❌ No            | ✅ Yes               | Duplicate chunks possible ; all fields can have multiple instances              |
| Vorbis  | ✅ Yes           | ✅ Yes               | Allows repeated field names; semantically meaningful for multi-value fields     |

**Vorbis Case Sensitive Handling**
Vorbis Comments are case-sensitive for field names but the library treats `ARTIST`, `Artist` and `artist` as the same field.
Thus if a file contains multiple `ARTIST` fields with different casing, they will be treated equally as different artists.
If a file contains 'TITLE' and 'Title' fields, the first one encountered will be used as the title, regardless of casing.

##### Single field with separated values (separator-based)

All values are stored in one field, separated by a character or delimiter.

Example:

```
ARTIST=Artist 1; Artist 2
```

- Used when repeated fields aren’t officially supported, though repeated fields could still occur in these formats.
- In ID3v2.4, the official separator is a null byte (\\0).

| Format  | Separator(s)   | Notes                                                       |
| ------- | -------------- | ----------------------------------------------------------- |
| ID3v1   | `/`, `;`, `,`  | Single field only; multi-values concatenated with separator |
| ID3v2.3 | `/`, `;`       | Uses single frame with separators                           |
| ID3v2.4 | `/`, `;`, `\0` | Null-separated values preferred;                            |
| RIFF    | `/`, `;`       | Not standardized; concatenation varies by implementation    |
| Vorbis  | rare, `\0`     | Native repeated fields make, sometimes null-separated       |

##### Reading Semantically Multiple Values

The library uses **smart semantic multi-value reading logic** that follows a two-step process to handle the complex variations in how metadata can be stored:

**Step 1: Extract All Field Instances**

For each metadata format present in the file, the library first extracts all individual field instances without any processing:

- **Vorbis (FLAC)**: Multiple `ARTIST=value` entries or single entry → `["Artist One", "Artist Two", "Artist Three"]` or `["Artist One;Artist Two;Artist Three"]`
- **ID3v2 (MP3)**: Multiple `TPE1` frames or single frame → `["Artist One;Artist Two"]` or `["Artist One", "Artist Two"]`
- **RIFF (WAV)**: Multiple `IART` chunks or single chunk → `["Artist One;Artist Two"]` or `["Artist One", "Artist Two"]`
- **ID3v1**: Single artist field → `["Artist One;Artist Two"]`

**Step 2a - If Null Separator: Apply Null Value Separation (ID3v2.4, Vorbis)**

- Extracted data: `["Artist One\0Artist Two", "Artist Three"]`
- Result after null separation: `["Artist One", "Artist Two", "Artist Three"]`

**Step 2b - Else If One Entry: Apply Smart Multi-Value Logic**

- **Multiple instances found**: Uses all instances as-is (no separator parsing)
  - Raw data: `["Artist One", "Artist; with; semicolons", "Artist Three"]`
  - Result: `["Artist One", "Artist; with; semicolons", "Artist Three"]`
  - ✅ Preserves separators within individual entries

- **Single instance found**: Applies smart separator parsing
  - Raw data: `["Artist One;Artist Two;Artist Three"]`
  - Result: `["Artist One", "Artist Two", "Artist Three"]`
  - ✅ Parses concatenated values using separator detection

- **Mixed instances found**: Uses all instances as-is (no separator parsing)
  - Raw data: `["Artist One", "Artist Two;Artist Three", "Artist Four"]`
  - Result: `["Artist One", "Artist Two;Artist Three", "Artist Four"]`
  - ✅ Preserves all entries exactly as found, including separators within values

###### Smart separator parsing of concatenated values

When parsing concatenated values from a single instance, the library uses an intelligent separator detection mechanism:

1. `//` (double slash)
2. `\\` (double backslash)
3. `;` (semicolon)
4. `\` (backslash)
5. `/` (forward slash)
6. `,` (comma)

###### Detailed Examples of Smart Semantically Multi-Value Logic

```python
# Example 1: Semantically multi-value field with multiple instances (no parsing needed)
# Step 1: Extract from Vorbis: ["Artist One", "Artist; with; semicolons", "Artist Three"]
# Step 2: Multi-value field + Multiple instances → Use as-is
# Result: ["Artist One", "Artist; with; semicolons", "Artist Three"]
# ✅ Separators preserved because they're part of actual artist names

# Example 2: Semantically multi-value field with single instance (parsing applied)
# Step 1: Extract from ID3v1: ["Artist One;Artist Two;Artist Three"]
# Step 2: Multi-value field + Single instance → Apply separator parsing
# Result: ["Artist One", "Artist Two", "Artist Three"]
# ✅ Concatenated string gets split into individual artists

# Example 3: Semantically multi-value field with multi instances and null separators (null separator parsing aplied)
# Step 1: Extract from ID3v2.4: ["Artist One\0Artist Two", "Artist Three"]
# Step 2: Multi-value field + Null separator → Apply null separation
# Result: ["Artist One", "Artist Two", "Artist Three"]
# ✅ Null-separated values correctly split into individual artists

# Example 4: Semantically single-value field with multiple instances (first only)
# Step 1: Extract from ID3v2: ["Main Title", "Alternative Title", "Extended Title"]
# Step 2: Single-value field → Take first value only
# Result: "Main Title"
# ✅ Only the first title is returned regardless of other instances

# Example 5: Semantically single-value field with parsing attempt (first only)
# Step 1: Extract from RIFF: ["Main Title;Alternative Title"]
# Step 2: Single-value field → Take first value (no parsing for single-value fields)
# Result: "Main Title;Alternative Title"
# ✅ Returns entire string as-is for single-value fields
```

##### Writing Semantically Multiple Values

###### Strategy Overview

The library uses a **smart writing strategy** that adapts to format capabilities and data characteristics. For each semantically multi-value field, different formats use different approaches:

| Format  | Multi-value Writing Method |
| ------- | -------------------------- |
| ID3v1   | Restricted smart separator |
| ID3v2.3 | Smart separator            |
| ID3v2.4 | Null-separated values      |
| RIFF    | Smart separator            |
| Vorbis  | Multiple entries           |

- The library automatically selects the best separator for legacy formats.
- Writing new values always replaces any previous values for that field.

##### Writing Duplicate Values

When writing duplicate values, the library won't preserve them.

```python
from audiometa import update_metadata

update_metadata("song.wav", {"artists": ["Artist One", "Artist Two", "Artist One", "Artist Three", "Artist Two"]})
# Result: "Artist One;Artist Two;Artist Three"
```

##### Automatic Empty Value Filtering

The library automatically filters out empty strings and `None` values from list-type metadata fields before writing. If all values in a list are filtered out, the field is removed entirely (set to `None`). This ensures clean metadata without empty or invalid entries across all supported formats.

```python
from audiometa import update_metadata

# Example 1: Empty values are automatically filtered out
metadata = {
    "artists": ["", "Artist 1", "   ", "Artist 2", None]
}
update_metadata("song.mp3", metadata)
# Results in: ["Artist 1", "Artist 2"] - empty strings and None filtered out

# Example 2: If all values are empty, the field is removed
metadata = {
    "artists": ["", "   ", None]
}
update_metadata("song.mp3", metadata)
# Results in: artists field is set to None (field removed)

# Example 3: Mixed valid and empty values
metadata = {
    "genres": ["Rock", "", "Pop", None, "Jazz"]
}
update_metadata("song.mp3", metadata)
# Results in: ["Rock", "Pop", "Jazz"] - only valid values preserved
```

##### Smart Separator Selection

When writing to legacy formats that require concatenated values, the library uses **intelligent separator selection**. It scans the values to be written and selects a separator that does not appear in any of the values, prioritizing more distinctive separators first:

0. `\0` (null byte) - used only in ID3v2.4
1. `//` (double slash) - highest priority
2. `\\` (double backslash)
3. `;` (semicolon)
4. `\` (backslash)
5. `/` (forward slash)
6. `,` (comma) - lowest priority

If all these separators are present in the values, a comma (`,`) is used as a last resort.

**ID3v1 Restricted Separator Selection:**
ID3v1 only allows a single separator character (not multi-character like `//` or `\\`). The library will select the first available single-character separator from the priority list that does not appear in any value:

1. `,` (comma) - Standard, readable
2. `;` (semicolon) - Common alternative
3. `|` (pipe) - Less common
4. `·` (middle dot) - Unicode but Latin-1 safe
5. `/` (slash) - Last resort, may be confusing

**ID3v2.4 Null Separator:**
For ID3v2.4, the library uses null bytes (`\0`) as the separator for multi-value fields, as per the specification.

##### Examples of Smart Separator Selection:

```python
# Example 1: Clean values - uses highest priority separator
values = ["Artist One", "Artist Two", "Artist Three"]
# Result: "Artist One//Artist Two//Artist Three" (uses //)

# Example 2: Values contain // - uses next priority separator
values = ["Artist//One", "Artist Two", "Artist Three"]
# Result: "Artist//One\\Artist Two\\Artist Three" (uses \\)

# Example 3: Values contain // and \\ - uses semicolon
values = ["Artist//One", "Artist\\Two", "Artist Three"]
# Result: "Artist//One;Artist\\Two;Artist Three" (uses ;)

# Example 4: All common separators present - uses comma
values = ["Artist//One", "Artist\\Two", "Artist;Three", "Artist/Four"]
# Result: "Artist//One,Artist\\Two,Artist;Three,Artist/Four" (uses ,)

# Example 5: ID3v1 restricted separator selection
values = ["Artist,One", "Artist;Two", "Artist|Three", "Artist·Four"]
# Result: "Artist,One/Artist;Two/Artist|Three/Artist·Four" (uses / as last resort)

# Example 6: ID3v2.4 null-separated values
values = ["Artist One", "Artist Two", "Artist Three"]
# Result: "Artist One\0Artist Two\0Artist Three" (uses null byte)
```

### Genre Handling

AudioMeta provides comprehensive genre support across all audio formats, with intelligent handling of genre codes, multiple genres, and format-specific limitations.

#### Genre Support by Format

##### Genre Support Matrix

| Format      | Multiple | Id3v1 Codes | Code + Text | Custom Text |
| ----------- | -------- | ----------- | ----------- | ----------- |
| **ID3v1**   | ❌       | ✅          | ❌          | ❌          |
| **ID3v2.3** | ✅       | ✅          | ✅          | ✓           |
| **ID3v2.4** | ✅       | ✓           | ✓           | ✅          |
| **Vorbis**  | ✅       | ❌          | ❌          | ✅          |
| **RIFF**    | ✓        | ✓           | ✓           | ✅          |

##### ID3v1 Genre Support

ID3v1 provides the most limited genre support with a fixed set of predefined genres.

**Genre Storage:**

- **Format**: Single byte numeric code (0-255)
- **Multiple Genres**: Not supported - only one genre per file
- **Custom Genres**: Not supported - must use predefined codes
- **Code Range**: 0-147 standard, 148-191 Winamp extensions, 192-255 unused

**Examples:**

- Code `17` → "Rock"
- Code `255` → Unknown/unspecified genre

##### ID3v2.3 Genre Support

ID3v2.3 uses the TCON (Content type) frame for genre information, following the ID3v2.3.0 specification.

**Genre Storage:**

- **Format**: Numeric string with optional parentheses notation
- **Multiple Genres**:
- Supported via consecutive parentheses (e.g., "(51)(39)") or with text (e.g., "(17)Rock(6)Blues")
- Unofficially supported via separators (e.g., "(17)Rock/(6)Blues") or multiple entries
- **Custom Genres**: Not officially supported, but widely used

**Examples:**

- `"(17)"` → Rock (code 17)
- `"(51)(39)"` → Trance + Cover (multiple codes)
- `"(17)Rock(6)Blues"` → Rock + Blues (code + text)
- `"(17)/(6)"` → Rock + Blues (separator-based, unofficial)
- `"(17)Rock; (6)Blues"` → Rock + Blues (separator-based, unofficial)
- `"Rock"` → Direct text genre (unofficial)
- `"Rock/Blues"` → Multiple text genres (unofficial)
- `"Grime"` → Direct custom genre (unofficial)

##### ID3v2.4 Genre Support

ID3v2.4 provides the most flexible genre support among ID3v2 versions.

**Genre Storage:**

- **Format**: UTF-8 encoded text with null-byte separation for multiple values
- **Multiple Genres**:
  - Full support using null-separated values
  - Unofficially supports separators (e.g., "Rock/Blues") for compatibility
  - Unofficially supports multiple TCON frames
- **Custom Genres**: Unlimited custom genre names
- **Backward Compatibility**: Can still use ID3v2.3 style parentheses notation but isn't recommended

**Examples:**

- `"Rock"` → Direct text genre
- `"Rock/0Blues"` → Multiple text genres null-separated
- `"Rock/Blues"` → Multiple text genres (separator-based, unofficial)
- Multiple TCON frames: `"Rock"` and `"Alternative"` → Multiple genres (unofficial)
- `"(17)"` → Rock (not recommended)
- `"(51)(39)"` → Trance + Cover (not recommended)
- `"(17)Rock(6)Blues"` → Rock + Blues (not recommended)
- `"(17)/(6)"` → Rock + Blues (not recommended)
- `"(17)Rock; (6)Blues"` → Rock + Blues (not recommended)

##### Vorbis Genre Support

Vorbis comments (used in FLAC files) provide text-based genre storage with full Unicode support.

**Genre Storage:**

- **Format**: UTF-8 text comments
- **Multiple Genres**:
  - Multiple GENRE fields
  - Separators (unofficial)
- **Format**: Unlimited custom genre names

**Examples:**

- Multiple fields: `"GENRE=Rock"` and `"GENRE=Alternative"` (official)
- `"GENRE=Rock; Alternative; Indie"` → Semicolon-separated genres (unofficial)

##### RIFF Genre Support

RIFF INFO chunks support both numeric codes and text genres.

**Genre Storage:**

- **Format**: IGNR chunk containing either text (official) or numeric code (unofficial) or mixed (unofficial)
- **Multiple Genres**:
  - Limited - typically single value, but text mode can use separators
  - Multiple entries can be present but are not standard

**Examples:**

- `"Rock"` → Single genre (official)
- `"Rock; Alternative; Indie"` → Multiple text genres (unofficial)
- `"17"` → Rock (code 17, unofficial)
- `"17; 20; 131"` → Rock + Alternative + Indie (codes with separators, unofficial)
- `"Rock; 20; Indie"` → Mixed names and codes (unofficial)

#### ID3v1 Genre Code System

ID3v1 uses a standardized genre code system (also used by RIFF) with 192 predefined genres:

- **Genres 0-79**: Original ID3v1 specification
- **Genres 80-125**: Winamp extensions
- **Genres 126-147**: Other players' extensions
- **Genres 148-191**: Winamp 5.6 extensions (November 2010)
- **Code 255**: Unknown/unspecified genre

An exhaustive list of all genre codes is available [here](audiometa/utils/id3v1_genre_code_map.py).

**Popular Genres:**

```python
# Common genre codes
0: "Blues"
17: "Rock"
18: "Techno"
25: "Euro-Techno"
32: "Classical"
80: "Folk"
131: "Indie"
189: "Dubstep"
```

#### Reading and Writing Strategy

##### Reading Genres

When reading genres, AudioMeta intelligently handles all the variations across formats, returning a consistent list of genre names.

It proceeds as follows:

1. Extract all genre entries from the file
2. If one entry, applies separator parsing if needed:
   1. If text with separators (e.g., "Rock/Blues", "Rock; Alternative", "(17)Rock/(6)Blues"), split using smart separator logic
   2. If codes or code+text without separators (e.g., "(17)(6)", "(17)Rock(6)Blues", "(17)Rock(6)"), separate accordingly conserving codes and names
3. Convert any genre codes or codes + names to names using the ID3v1 genre code map
   1. For code + text entries, use text part only for more flexibility
4. Return a list of unique genre names

**Note**: According to global multi-value logic, if multiple genre entries are found, they are returned as-is without separator parsing.

##### Writing Genres

When writing genres, AudioMeta uses a smart strategy based on the target format's capabilities:

###### Writing Genres for ID3v1

- Selects the first genre from the provided list and converts it to the corresponding ID3v1 code
- If no matching code is found, sets genre to `255` (unknown)

###### Writing Genres for ID3v2.3

- If all genres have corresponding ID3v1 codes, uses parentheses notation (with text if available)
- If any genre lacks a code, uses separator-based text format with smart separator selection

###### Writing Genres for ID3v2.4

- Writes all genres as null-separated text values

###### Writing Genres for Vorbis

- Writes each genre name as a separate GENRE entry

###### Writing Genres for RIFF

- Writes genres as text using smart separator selection

### Rating Handling

AudioMeta implements a sophisticated rating profile system to handle the complex compatibility requirements across different audio players and formats. This system ensures that ratings work consistently regardless of which software was used to create them.

#### The Rating Profile Problem

**The Problem**: Different audio players use completely different numeric values for the same star ratings. For example, a 3-star rating can be stored as:

- `128` (Windows Media Player, MusicBee, Winamp)
- `60` (FLAC players, Vorbis)
- `153` (Traktor)

> 📋 **Complete Compatibility Table**: See [`rating_profiles.py`](audiometa/utils/rating_profiles.py) for the detailed reference table showing all player compatibility and exact numeric values.

**Key Points:**

- **0/None ratings**: `0` can mean either "no rating" (Traktor) or "0 stars" (MusicBee) - AudioMeta distinguishes between them and handles "no rating" cases
- **Half-star support**: Limited support - mainly MusicBee and some ID3v2 implementations
- **Traktor limitation**: Only supports whole stars (1, 2, 3, 4, 5)
- **Format compatibility**: Different formats use different rating systems
- **Automatic handling**: AudioMeta manages all the complexity for you

#### Rating Profile Types

AudioMeta recognizes three main rating profiles:

**Profile A: 255 Non-Proportional (Most Common)**

- Used by: ID3v2 (MP3), RIFF (WAV), most standard players
- Examples: Windows Media Player, MusicBee, Winamp, kid3
- **Half-star support**: ✅ Full support (0.5, 1.5, 2.5, 3.5, 4.5 stars)

**Profile B: 100 Proportional (FLAC Standard)**

- Used by: Vorbis (FLAC), some WAV ID3v2 implementations
- Examples: FLAC files, some modern players
- **Half-star support**: ✅ Full support (0.5, 1.5, 2.5, 3.5, 4.5 stars)

**Profile C: 255 Proportional (Traktor)**

- Used by: Traktor software (Native Instruments)
- For MP3 ID3v2 and FLAC Vorbis (Traktor does not write tags on WAV files)
- Examples: Traktor Pro, Traktor DJ
- **Half-star support**: ❌ No support (only whole stars: 1, 2, 3, 4, 5)

#### Rating Normalization

AudioMeta supports two modes for handling ratings:

1. **Raw Mode** (default): Returns and accepts raw profile-specific values
2. **Normalized Mode**: Converts between raw values and a normalized scale

```python
from audiometa import get_unified_metadata, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat

# Reading without normalization (raw values)
metadata = get_unified_metadata("song.mp3")
rating = metadata.get(UnifiedMetadataKey.RATING)  # Returns: 128, 60, 153, etc. (raw profile values)

# Reading with normalization
metadata = get_unified_metadata("song.mp3", normalized_rating_max_value=10)
rating = metadata.get(UnifiedMetadataKey.RATING)  # Returns: 0, 2, 4, 6, 8, 10 (normalized)

# Writing without normalization (raw values)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 128}, metadata_format=MetadataFormat.ID3V2)  # Direct raw value

# Writing with normalization
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 6}, normalized_rating_max_value=10)  # Writes 128 (Profile A)
update_metadata("song.flac", {UnifiedMetadataKey.RATING: 6}, normalized_rating_max_value=10)  # Writes 60 (Profile B)
```

**Normalization Formula**:

- **Reading**: `normalized_rating = star_rating_base_10 * normalized_rating_max_value / 10`
  - Example: 3 stars (star_rating_base_10=6) with max=100 → `6 * 100 / 10 = 60`
- **Writing**: `star_rating_base_10 = int((normalized_rating * 10) / normalized_rating_max_value)`
  - Example: normalized_rating=60 with max=100 → `int((60 * 10) / 100) = 6` → Profile A writes 128

**Benefits of Normalization**:

- Consistent values across different rating profiles
- Easy to work with regardless of source player
- Flexible scale (can use 0-10, 0-100, 0-255, etc.)

**When to Use Each Mode**:

- **Normalized**: When you want consistent, player-agnostic rating values
- **Raw**: When you need direct control over the exact profile values written to files

#### Normalized Rating Scale

When `normalized_rating_max_value` is provided, AudioMeta uses a normalized scale. With `normalized_rating_max_value=10`, the scale is:

```python
# 0 = No rating
# 2 = 1 star
# 4 = 2 stars
# 6 = 3 stars
# 8 = 4 stars
# 10 = 5 stars

# Reading with normalization
metadata = get_unified_metadata("song.mp3", normalized_rating_max_value=10)
rating = metadata.get('rating')  # Returns 0-10 scale

# Writing with normalization
update_metadata("song.mp3", {"rating": 8}, normalized_rating_max_value=10)  # 4 stars
```

**Note**: Without `normalized_rating_max_value`, AudioMeta returns raw profile-specific values (e.g., 128, 60, 153) instead of normalized values.

#### How AudioMeta Handles Rating Profiles

##### Reading Ratings

**Automatic Profile Detection**

```python
from audiometa import get_unified_metadata

# AudioMeta automatically detects the rating profile
# Without normalization: returns raw profile values
metadata = get_unified_metadata("song.mp3")
rating = metadata.get('rating')  # Returns raw values: 128, 60, 153, etc.

# With normalization: returns consistent normalized values
metadata = get_unified_metadata("song.mp3", normalized_rating_max_value=10)
rating = metadata.get('rating')  # Returns 0-10 scale: 0, 2, 4, 6, 8, 10, etc.

# Examples of what you get with normalization (normalized_rating_max_value=10):
# - File rated 3 stars in Windows Media Player (128) → rating = 6
# - File rated 3 stars in FLAC player (60) → rating = 6
# - File rated 3 stars in Traktor (153) → rating = 6
# - File rated 3.5 stars in MusicBee (186) → rating = 7
# - File rated 2.5 stars in FLAC (50) → rating = 5

# Examples without normalization:
# - File rated 3 stars in Windows Media Player → rating = 128 (raw)
# - File rated 3 stars in FLAC player → rating = 60 (raw)
# - File rated 3 stars in Traktor → rating = 153 (raw)
```

##### Writing Ratings

##### Rating Writing Profiles

AudioMeta uses two write profiles to ensure maximum compatibility across different audio players:

- **BASE_255_NON_PROPORTIONAL** (Profile A): Used for ID3v2 (MP3) and RIFF (WAV)
  - Values: `[0, 13, 1, 54, 64, 118, 128, 186, 196, 242, 255]`
  - Most widely supported profile
  - Full half-star support (0.5, 1.5, 2.5, 3.5, 4.5 stars)

- **BASE_100_PROPORTIONAL** (Profile B): Used for Vorbis (FLAC)
  - Values: `[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]`
  - Standard for FLAC files
  - Full half-star support (0.5, 1.5, 2.5, 3.5, 4.5 stars)

AudioMeta automatically selects the appropriate profile based on the file format:

```python
from audiometa import update_metadata

# AudioMeta automatically uses the most compatible profile for each metadata format
update_metadata("song.mp3", {"rating": 6})   # ID3v2 uses BASE_255_NON_PROPORTIONAL (128)
update_metadata("song.flac", {"rating": 6})  # Vorbis uses BASE_100_PROPORTIONAL (60)
update_metadata("song.wav", {"rating": 6})   # RIFF uses BASE_255_NON_PROPORTIONAL (128)

# Half-star ratings are also supported:
update_metadata("song.mp3", {"rating": 7})   # 3.5 stars → BASE_255_NON_PROPORTIONAL (186)
update_metadata("song.flac", {"rating": 5})  # 2.5 stars → BASE_100_PROPORTIONAL (50)
```

##### Rating Validation Rules

AudioMeta validates rating values based on whether normalization is enabled:

**When `normalized_rating_max_value` is not provided (raw mode)**:

The rating value is written as-is. Any non-negative integer value (>= 0) is allowed.

```python
from audiometa import update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat

# Any non-negative integer rating value is allowed when normalized_rating_max_value is not provided
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 128}, metadata_format=MetadataFormat.ID3V2)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 75}, metadata_format=MetadataFormat.ID3V2)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 0}, metadata_format=MetadataFormat.ID3V2)
update_metadata("song.flac", {UnifiedMetadataKey.RATING: 50}, metadata_format=MetadataFormat.VORBIS)
update_metadata("song.flac", {UnifiedMetadataKey.RATING: 128}, metadata_format=MetadataFormat.VORBIS)

# Invalid: negative values are rejected
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: -1}, metadata_format=MetadataFormat.ID3V2)
# Error: Rating value -1 is invalid. Rating values must be non-negative (>= 0)
```

**When `normalized_rating_max_value` is provided (normalized mode)**:

The rating value is normalized and must map to a valid profile value. AudioMeta calculates `(value / max) * 100` and `(value / max) * 255`, then checks if at least one of these rounded values exists in a supported writing profile (BASE_100_PROPORTIONAL or BASE_255_NON_PROPORTIONAL).

```python
# Valid: 50/100 * 100 = 50, which is in BASE_100_PROPORTIONAL profile
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 50}, normalized_rating_max_value=100)

# Invalid: 37/100 * 100 = 37 (not in BASE_100_PROPORTIONAL)
# 37/100 * 255 = 94 (not in BASE_255_NON_PROPORTIONAL)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 37}, normalized_rating_max_value=100)
# Error: Rating value 37 is not valid for max value 100. Calculated output values (37 for 100-scale, 94 for 255-scale) do not exist in any supported writing profile.

# Invalid: negative values are rejected
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: -1}, normalized_rating_max_value=100)
# Error: Rating value -1 is invalid. Rating values must be non-negative (>= 0)

# Invalid: values above max are rejected
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 101}, normalized_rating_max_value=100)
# Error: Rating value 101 is out of range. Value must be between 0 and 100 (inclusive)

# With max=10, any integer 0-10 is valid (all map to valid profile values)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 7}, normalized_rating_max_value=10)

# With max=255, valid values include those that map to BASE_255_NON_PROPORTIONAL or BASE_100_PROPORTIONAL
# Examples: 0, 1, 13, 25, 50, 54, 64, 76, 102, 118, 128, 153, 178, 186, 196, 204, 229, 242, 255
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 128}, normalized_rating_max_value=255)  # Valid: maps to 128 in BASE_255_NON_PROPORTIONAL
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 50}, normalized_rating_max_value=255)   # Valid: maps to 20 in BASE_100_PROPORTIONAL
```

#### Half-Star Rating Support

AudioMeta fully supports half-star ratings (0.5, 1.5, 2.5, 3.5, 4.5 stars) across all the formats:

```python
# Reading half-star ratings
metadata = get_unified_metadata("half_star_rated.mp3")
rating = metadata.get('rating')  # Could be 1.0, 3.0, 5.0, 7.0, 9.0 for half-stars

# Writing half-star ratings
update_metadata("song.mp3", {"rating": 7})   # 3.5 stars
update_metadata("song.flac", {"rating": 5})  # 2.5 stars
update_metadata("song.wav", {"rating": 9})   # 4.5 stars
```

**Why profile-based validation?**

When normalization is enabled, ratings are converted to file-specific values using the writing profiles (BASE_100_PROPORTIONAL for Vorbis, BASE_255_NON_PROPORTIONAL for ID3v2/RIFF). The validation ensures that the normalized value maps to an actual profile value that can be written to the file. This guarantees that the rating will be correctly interpreted by audio players that follow these standard profiles.

**Error Handling**:

Invalid rating values raise `InvalidRatingValueError` with a descriptive message indicating why the value is invalid.

### Track Number

The library handles different track number formats across audio metadata standards:

#### ID3v1 Track Number Format

ID3v1 does not natively support track numbers. The library supports storing track numbers in the comment field since ID3v1.1 format.

- **Format**: Simple numeric string (e.g., `"5"`, `"12"`)
- **Parsing**: Returns as string
- **Examples**:
  - `"5"` → Track number: `"5"`
  - `"12"` → Track number: `"12"`

#### ID3v2 Track Number Format

- **Format**: `"track/total"` (e.g., `"5/12"`, `"99/99"`) or simple `"track"` (e.g., `"5"`, `"1"`)
- **Parsing**: Returns the full track number string as stored
- **Examples**:
  - `"5/12"` → Track number: `"5/12"`
  - `"99/99"` → Track number: `"99/99"`
  - `"1"` → Track number: `"1"` (simple format also supported)

#### Vorbis Track Number Format

- **Format**: Simple numeric string (e.g., `"5"`, `"12"`)
- **Parsing**: Returns as string
- **Examples**:
  - `"5"` → Track number: `"5"`
  - `"12"` → Track number: `"12"`

#### RIFF Track Number Format

- **Format**: Simple numeric string (e.g., `"5"`, `"12"`)
- **Parsing**: Returns as string
- **Examples**:
  - `"5"` → Track number: `"5"`
  - `"12"` → Track number: `"12"`

#### Reading And Writing Track Number

##### Reading Track Number

The library returns track numbers as strings. The library handles common edge cases:

- `"5/"` → Track number: `"5/"` (trailing slash preserved)
- `"/12"` → Track number: `None` (no track number before slash)
- `"abc/def"` → Track number: `None` (non-numeric values)
- `""` → Track number: `None` (empty string)
- `"5/12/15"` → Track number: `None` (multiple slashes, invalid format)
- `"5-12"` → Track number: `"5-12"` (different separator preserved)
- `"01"` → Track number: `"01"` (leading zeros preserved)

##### Writing Track Number

The library supports writing track numbers in various formats. For formats that support track totals, the full format is preserved. The following matrix shows what value is written for each input format:

| Input Value | ID3v1  | ID3v2     | Vorbis    | RIFF      |
| ----------- | ------ | --------- | --------- | --------- |
| `5` (int)   | `"5"`  | `"5"`     | `"5"`     | `"5"`     |
| `"5"` (str) | `"5"`  | `"5"`     | `"5"`     | `"5"`     |
| `"5/12"`    | `"5"`  | `"5/12"`  | `"5/12"`  | `"5/12"`  |
| `"99/99"`   | `"99"` | `"99/99"` | `"99/99"` | `"99/99"` |
| `"1"`       | `"1"`  | `"1"`     | `"1"`     | `"1"`     |

**Notes:**

- **ID3v1**: Only supports track numbers (1-255), extracts the track number from formats like "5/12" and ignores the total
- **ID3v2**: Supports full track/total format (e.g., "5/12") as per ID3v2 specification
- **Vorbis**: Supports full track/total format through TRACKNUMBER field
- **RIFF**: Track number writing is not currently supported

### Lyrics Support

Two types of lyrics are supported: synchronized lyrics (synchronized with music, for karaoke) and unsynchronized lyrics (plain text).

#### Synchronized Lyrics

TODO: Implement synchronized lyrics support in future versions.

#### Unsynchronized Lyrics

Unsynchronized lyrics are supported differently across formats:

##### ID3v1 Unsynchronized Lyrics

ID3v1 does not support unsynchronized lyrics due to its limited structure.

##### ID3v2 Unsynchronized Lyrics

ID3v2 supports unsynchronized lyrics through the `USLT` (Unsynchronized Lyrics/Text transcription) frame. Multiple `USLT` frames can be used to store lyrics in different languages or formats within the same file.

The library does not currently support language codes or multiple lyrics entries and will write only a single `USLT` frame with default language code `eng`.

TODO: Implement full multi-language support in future versions.

##### RIFF Unsynchronized Lyrics

RIFF INFO chunks do not have native support for lyrics. The library supports storing unsynchronized lyrics in the `UNSYNCHRONIZED_LYRICS` chunk.

It does not support language codes or multiple lyrics entries due to lack of standardization.

##### Vorbis Unsynchronized Lyrics

Vorbis comments support lyrics through the `UNSYNCHRONIZED_LYRICS` field.
It does not support language codes or multiple lyrics entries due to lack of standardization.

#### Synchronized Lyrics

Synchronized lyrics (SYLT frames in ID3v2) are not currently supported by the library.

### Unsupported Metadata Handling

The library handles unsupported metadata consistently across all strategies:

- **Forced format** (when `metadata_format` is specified): Always fails fast by raising `MetadataFieldNotSupportedByMetadataFormatError` for any unsupported field. **No writing is performed** - the file remains completely unchanged.
- **All strategies (SYNC, PRESERVE, CLEANUP) with `fail_on_unsupported_field=False` (default)**: Handle unsupported fields gracefully by logging warnings and continuing with supported fields
- **All strategies (SYNC, PRESERVE, CLEANUP) with `fail_on_unsupported_field=True`**: Fails fast if any field is not supported by the target format. **No writing is performed** - the file remains completely unchanged (atomic operation).

#### Format-Specific Limitations {#format-specific-limitations-unsupported}

| Format         | Forced Format                     | All Strategies (SYNC, PRESERVE, CLEANUP) with `fail_on_unsupported_field=False` | All Strategies with `fail_on_unsupported_field=True` |
| -------------- | --------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------- |
| **RIFF (WAV)** | Always fails fast, **no writing** | Logs warnings for unsupported fields, writes supported ones                     | Fails fast for unsupported fields, **no writing**    |
| **ID3v1**      | Always fails fast, **no writing** | Logs warnings for unsupported fields, writes supported ones                     | Fails fast for unsupported fields, **no writing**    |
| **ID3v2**      | Always fails fast, **no writing** | All fields supported                                                            | All fields supported                                 |
| **Vorbis**     | Always fails fast, **no writing** | All fields supported                                                            | All fields supported                                 |

#### Atomic Write Operations

When `fail_on_unsupported_field=True` is used, the library ensures **atomic write operations**:

- **All-or-nothing behavior**: Either all metadata is written successfully, or nothing is written at all
- **File integrity**: If any field is unsupported, the file remains completely unchanged
- **No partial updates**: Prevents inconsistent metadata states where only some fields are updated
- **Error safety**: Ensures that failed operations don't leave files in a partially modified state

This atomic behavior is crucial for:

- **Data integrity**: Prevents corruption from partial writes
- **Consistency**: Ensures metadata is always in a valid state
- **Reliability**: Makes operations predictable and safe to retry
- **Debugging**: Clear failure modes make issues easier to diagnose

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

### None vs Empty String Handling

The library handles `None` and empty string values differently across audio formats:

| Format            | Setting to `None`        | Setting to `""` (empty string)   | Read Back Result               |
| ----------------- | ------------------------ | -------------------------------- | ------------------------------ |
| **ID3v2 (MP3)**   | Removes field completely | Removes field completely         | `None` / `None`                |
| **Vorbis (FLAC)** | Removes field completely | Creates field with empty content | `None` / `""`                  |
| **RIFF (WAV)**    | Removes field completely | Removes field completely         | `None` / `None`                |
| **ID3v1 (MP3)**   | ✅ **Supported**         | ✅ **Supported**                 | Legacy format with limitations |

#### Example

```python
from audiometa import update_metadata, get_unified_metadata_field

# MP3 file - same behavior for None and empty string
update_metadata("song.mp3", {"title": None})
title = get_unified_metadata_field("song.mp3", "title")
print(title)  # Output: None (field removed)

# FLAC file - different behavior for None vs empty string
update_metadata("song.flac", {"title": None})
title = get_unified_metadata_field("song.flac", "title")
print(title)  # Output: None (field removed)

update_metadata("song.flac", {"title": ""})
title = get_unified_metadata_field("song.flac", "title")
print(title)  # Output: "" (field exists but empty)
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
- mutagen >= 1.45.0
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
