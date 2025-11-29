# Metadata Formats Guide

This document provides comprehensive information about the metadata formats supported by AudioMeta, including their history, structure, advantages, disadvantages, and use cases.

## Table of Contents

- [ID3v1](#id3v1-metadata-format)
- [ID3v2](#id3v2-metadata-format)
- [Vorbis Comments](#vorbis-comments-metadata-format)
- [RIFF INFO](#riff-info-metadata-format)
- [Format Comparison](#format-comparison)
- [AudioMeta Implementation](#audiometa-implementation)

## ID3v1 Metadata Format

### Overview

ID3v1 is the original metadata format for MP3 files, introduced in 1996 by Eric Kemp. It was created to solve the problem of identifying MP3 files when they were transferred between systems, as filenames alone were insufficient.

### History

- **1996**: ID3v1 introduced - 128-byte fixed structure
- **1997**: ID3v1.1 introduced - Added track number support in comment field
- **Status**: Legacy format, still widely supported for backward compatibility

### Structure

ID3v1 uses a simple **128-byte fixed structure** appended to the end of MP3 files:

```
Offset  Length  Field
------  ------  ------
0       3       Header ("TAG")
3       30      Title (ASCII, null-padded)
33      30      Artist (ASCII, null-padded)
63      30      Album (ASCII, null-padded)
93      4       Year (ASCII, 4 digits)
97      30      Comment (ASCII, null-padded)
127     1       Genre (single byte, 0-255)
```

**ID3v1.1 Extension:**

- Track number stored in last byte of comment field (bytes 125-126)
- Comment reduced to 28 bytes (bytes 97-124)
- Last byte of comment (byte 125) = track number (0-255)
- Last byte of comment (byte 126) = null terminator

### Advantages

- ✅ **Simple**: Easy to implement and parse
- ✅ **Universal**: Supported by virtually all MP3 players and software
- ✅ **Backward Compatible**: Works with very old hardware and software
- ✅ **Small Overhead**: Only 128 bytes per file
- ✅ **No Corruption Risk**: Fixed size prevents file corruption

### Disadvantages

- ❌ **Limited Fields**: Only title, artist, album, year, comment, genre, track number
- ❌ **Fixed Lengths**: 30-character limit for text fields (very restrictive)
- ❌ **ASCII Only**: No Unicode support, limited character sets
- ❌ **Single Genre**: Only one genre code (0-255), no custom genres
- ❌ **No Album Artist**: Cannot distinguish between track artist and album artist
- ❌ **No Multiple Values**: Cannot store multiple artists or genres
- ❌ **No Extended Metadata**: No support for BPM, rating, composer, etc.
- ❌ **No Cover Art**: Cannot embed images

### Use Cases

- **Legacy Systems**: Old MP3 players and car stereos
- **Maximum Compatibility**: When you need metadata readable by any device
- **Simple Metadata**: When basic information (title, artist, album) is sufficient
- **File Size**: When minimizing metadata overhead is important

### Specifications

- **Official Spec**: [ID3v1 Specification](http://id3.org/ID3v1)
- **Genre Codes**: Standard 0-147, Winamp extensions 148-191

### AudioMeta Support

- **Read/Write**: Full support
- **File Types**: MP3 (native), FLAC, WAV (extended support)
- **Version**: ID3v1.1 (with track number support)
- **Implementation**: Direct file manipulation (no external dependencies)

---

## ID3v2 Metadata Format

### Overview

ID3v2 is the modern, extensible metadata format for MP3 files, designed to overcome ID3v1's limitations. It uses a flexible frame-based structure that can store extensive metadata including Unicode text, images, and custom fields.

### History

- **1998**: ID3v2.2 introduced - Three-character frame IDs (TT2, TP1, etc.)
- **1999**: ID3v2.3 introduced - Four-character frame IDs, improved structure
- **2000**: ID3v2.4 introduced - UTF-8 support, improved encoding, null-separated values
- **Status**: Current standard, ID3v2.3 most widely supported, ID3v2.4 preferred for new tags

### Structure

ID3v2 uses a **flexible frame-based structure** at the beginning of files:

```
ID3v2 Header (10 bytes)
├── Frame 1 (variable size)
│   ├── Frame ID (4 chars, e.g., "TIT2")
│   ├── Frame Size (4 bytes)
│   ├── Flags (2 bytes)
│   └── Frame Data (variable)
├── Frame 2 (variable size)
└── ...
```

**Key Components:**

- **Header**: Version, flags, tag size
- **Frames**: Individual metadata fields (TIT2=Title, TPE1=Artist, etc.)
- **Frame Types**: Text frames, URL frames, binary frames (images, audio)
- **Encoding**: ISO-8859-1 (v2.3), UTF-16 (v2.3), UTF-8 (v2.4)

### Versions

#### ID3v2.2

- Three-character frame IDs (TT2, TP1, TAL)
- ISO-8859-1 or UCS-2 encoding
- Less common but functional

#### ID3v2.3 (Most Common)

- Four-character frame IDs (TIT2, TPE1, TALB)
- UTF-16/UTF-16BE encoding
- TYER + TDAT for dates (year + date separately)
- Maximum compatibility across players

#### ID3v2.4 (Modern)

- Four-character frame IDs
- UTF-8 encoding (more efficient)
- TDRC frame for full timestamps (YYYY-MM-DD)
- Null-separated values for multiple entries
- Preferred for new tags

### Advantages

- ✅ **Extensive Fields**: Supports all common metadata fields plus custom fields
- ✅ **Unicode Support**: Full international character support (UTF-8 in v2.4)
- ✅ **Multiple Values**: Can store multiple artists, genres, etc.
- ✅ **Large Text**: Up to ~8MB per field (practical limit)
- ✅ **Binary Data**: Can embed cover art, images, audio samples
- ✅ **Extensible**: Custom frames via TXXX frames
- ✅ **Versatile**: Works with MP3, WAV, FLAC files
- ✅ **Rich Metadata**: Supports BPM, rating, composer, lyrics, etc.

### Disadvantages

- ❌ **Complex**: More complex to implement than ID3v1
- ❌ **Larger Overhead**: Variable size, can be several KB
- ❌ **Version Fragmentation**: Different versions have different features
- ❌ **Compatibility**: Older players may not support v2.4
- ❌ **Frame Limits**: Some players limit frame sizes or counts

### Use Cases

- **Modern MP3 Files**: Standard for new MP3 files
- **Rich Metadata**: When you need extensive metadata (BPM, rating, lyrics, etc.)
- **Multiple Artists**: When tracks have multiple artists or genres
- **Cover Art**: When embedding album artwork
- **Cross-Platform**: When working with MP3, WAV, and FLAC files
- **Professional Use**: When detailed metadata is required

### Specifications

- **Official Spec**: [ID3v2.3.0 Specification](https://id3.org/id3v2.3.0)
- **ID3v2.4 Spec**: [ID3v2.4.0 Specification](https://id3.org/id3v2.4.0-structure)
- **Frame List**: [ID3v2 Frame List](https://id3.org/id3v2.3.0#sec4)

### AudioMeta Support

- **Read/Write**: Full support
- **File Types**: MP3 (native), WAV, FLAC (extended support)
- **Versions**: ID3v2.3 (default, maximum compatibility), ID3v2.4 (optional)
- **Implementation**: Uses mutagen library
- **Default Version**: ID3v2.3 for maximum compatibility

---

## Vorbis Comments Metadata Format

### Overview

Vorbis Comments are a simple, flexible metadata system used in Ogg Vorbis, FLAC, and other Xiph.org formats. They use a key-value pair structure that's easy to read, write, and extend.

### History

- **2000**: Vorbis Comments introduced with Ogg Vorbis format
- **2001**: Adopted by FLAC (Free Lossless Audio Codec)
- **Status**: Standard metadata format for FLAC files

### Structure

Vorbis Comments use a **simple key-value pair structure**:

```
Vendor String (UTF-8)
Comment Count (32-bit integer)
├── Comment 1: "KEY=VALUE" (UTF-8)
├── Comment 2: "KEY=VALUE" (UTF-8)
└── ...
```

**Key Features:**

- **Case-Insensitive Keys**: "TITLE", "title", "Title" are equivalent
- **Multiple Values**: Multiple entries with same key allowed (e.g., multiple ARTIST entries)
- **UTF-8 Encoding**: Full Unicode support
- **Flexible**: Any key-value pairs allowed (standardized keys recommended)

### Standard Fields

Common standardized field names:

- `TITLE` - Track title
- `ARTIST` - Track artist(s)
- `ALBUM` - Album name
- `ALBUMARTIST` - Album artist(s)
- `DATE` - Release date (YYYY-MM-DD)
- `GENRE` - Genre(s)
- `TRACKNUMBER` - Track number
- `DISCNUMBER` - Disc number
- `DISCTOTAL` - Total discs
- `COMPOSER` - Composer(s)
- `COMMENT` - Comments
- `DESCRIPTION` - Description

### Advantages

- ✅ **Simple**: Easy to read and write, human-readable
- ✅ **Flexible**: Any key-value pairs, extensible
- ✅ **Multiple Values**: Native support for multiple artists, genres, etc.
- ✅ **Unicode**: Full UTF-8 support
- ✅ **No Size Limits**: Practical limits only (typically ~8MB per field)
- ✅ **Standardized**: Well-documented standard field names
- ✅ **Open Standard**: Xiph.org open specification

### Disadvantages

- ❌ **FLAC Only**: Primarily used in FLAC files (not MP3 or WAV)
- ❌ **No Binary Data**: Cannot embed images directly (FLAC uses separate picture blocks)
- ❌ **Case Sensitivity**: Keys are case-insensitive but implementations vary
- ❌ **No Structured Data**: Simple key-value only, no nested structures
- ❌ **Limited Standardization**: Some fields have multiple conventions

### Use Cases

- **FLAC Files**: Standard metadata format for FLAC
- **Lossless Audio**: Preferred format for lossless audio libraries
- **Multiple Values**: When you need multiple artists or genres
- **Open Source**: When working in open-source audio ecosystems
- **Simple Metadata**: When you prefer simple, readable metadata

### Specifications

- **Official Spec**: [Vorbis Comment Specification](https://xiph.org/vorbis/doc/v-comment.html)
- **FLAC Metadata**: [FLAC Format Specification](https://xiph.org/flac/format.html)

### AudioMeta Support

- **Read/Write**: Full support
- **File Types**: FLAC (native)
- **Implementation**: Uses mutagen library with custom parsing
- **Key Normalization**: Case-insensitive reading, uppercase writing for consistency

---

## RIFF INFO Metadata Format

### Overview

RIFF (Resource Interchange File Format) INFO chunks are the standard metadata format for WAV files. They use FourCC (Four Character Code) identifiers to store metadata in a structured chunk format.

### History

- **1991**: RIFF format introduced by Microsoft and IBM
- **1991**: WAV format introduced as RIFF subtype
- **Status**: Standard metadata format for WAV files

### Structure

RIFF uses a **chunk-based structure**:

```
RIFF Header
├── WAVE Header
├── fmt chunk (audio format)
├── LIST chunk
│   └── INFO chunk
│       ├── INAM (Title) - FourCC + size + data
│       ├── IART (Artist) - FourCC + size + data
│       ├── IPRD (Album) - FourCC + size + data
│       └── ...
├── bext chunk (BWF only - broadcast extension)
└── data chunk (audio data)
```

**Key Components:**

- **FourCC Codes**: 4-character identifiers (INAM, IART, IPRD, etc.)
- **Chunk Structure**: Each field is a sub-chunk with size and data
- **Word Alignment**: Data padded to word boundaries (2-byte alignment)
- **UTF-8 Encoding**: Modern implementations use UTF-8

**Note on `bext` chunk**: The `bext` chunk is a RIFF chunk (follows RIFF chunk structure), but it's separate from the RIFF INFO chunk system. It's a BWF-specific chunk that exists at the same level as `fmt`, `LIST`, and `data` chunks, not nested within the INFO chunk.

### Standard Fields (FourCC Codes)

Common RIFF INFO chunk fields:

- `INAM` - Title (Name)
- `IART` - Artist
- `IPRD` - Product (Album)
- `IAAR` - Album Artist
- `ICRD` - Creation Date (YYYY-MM-DD)
- `IGNR` - Genre
- `ITRK` - Track Number
- `ICMP` - Composer
- `ICOP` - Copyright
- `ICMT` - Comment
- `ILNG` - Language
- `IBPM` - BPM (non-standard, but used)
- `IRTD` - Rating (non-standard, but used)

### Advantages

- ✅ **Native WAV Format**: Standard metadata format for WAV files
- ✅ **Structured**: Well-defined chunk structure
- ✅ **Extensible**: Can add custom FourCC codes
- ✅ **Professional Use**: Used in professional audio applications
- ✅ **BWF Compatible**: Works with Broadcast Wave Format (BWF) extensions

**Note on BWF**: Broadcast Wave Format (BWF) files are WAV files that include a `bext` chunk. Adding a `bext` chunk to a WAV file makes it a BWF file. The `bext` chunk is a RIFF chunk (follows RIFF chunk structure) but is separate from the RIFF INFO chunk system - it exists at the same level as other top-level chunks like `fmt` and `data`. BWF files can contain both standard RIFF INFO chunks and the additional `bext` chunk for broadcast-specific metadata.

### Broadcast Wave Format (BWF) Versions

BWF has evolved through multiple versions, each adding new capabilities:

#### Version 0 (1997)

- **Initial Release**: Original BWF specification by European Broadcasting Union (EBU)
- **bext Chunk Structure**: Basic fields without UMID support
- **Version Field**: `0x0000` (as recommended by FADGI)
- **Fields**: Description, Originator, OriginatorReference, OriginationDate, OriginationTime, TimeReference, CodingHistory
- **UMID**: Not supported (64 bytes reserved for future use)

#### Version 1 (2001)

- **UMID Support**: Added Unique Material Identifier (UMID) as defined by SMPTE standard ST 330:2011
- **Version Field**: `0x0001`
- **Fields**: All v0 fields plus UMID (64 bytes)
- **Backward Compatible**: v1 files are readable by v0 implementations (UMID ignored)

#### Version 2 (2011)

- **Loudness Metadata**: Added audio loudness metadata fields aligned with EBU R-128 recommendation
- **Version Field**: `0x0002`
- **Fields**: All v1 fields plus loudness metadata:
  - LoudnessValue
  - LoudnessRange
  - MaxTruePeakLevel
  - MaxMomentaryLoudness
  - MaxShortTermLoudness
- **Backward Compatible**: v2 files are readable by v1/v0 implementations (loudness fields ignored)

**bext Chunk Structure (v1/v2):**

```
Offset  Size    Field
------  ----    -----
0       256     Description (ASCII, null-terminated)
256     32      Originator (ASCII, null-terminated)
288     32      OriginatorReference (ASCII, null-terminated)
320     10      OriginationDate (ASCII, YYYY-MM-DD)
330     8       OriginationTime (ASCII, HH:MM:SS)
338     8       TimeReference (uint64, little-endian)
346     2       Version (uint16, little-endian): 0x0000/0x0001/0x0002
348     64      UMID (binary, v1+ only)
412     190     Reserved (zeros, or loudness metadata in v2)
602+    var     CodingHistory (ASCII, null-terminated, variable length)
```

**Version Compatibility:**

- All versions are backward compatible
- Older implementations ignore unsupported fields
- Newer implementations assign default values to missing fields
- The Version field (2 bytes) indicates which BWF version is used

**BWF Field Support in Other Formats:**

Most BWF fields are BWF-specific and not natively supported by other metadata formats. The exception is **ISRC**, which is also supported by **ID3v2**: TSRC frame and **Vorbis**: ISRC field.

BWF fields are designed for professional broadcasting workflows and include specialized metadata (time references, UMID identifiers, loudness measurements) that are unique to the BWF specification and not found in consumer-oriented formats like ID3v2 or Vorbis.

### Disadvantages

- ❌ **WAV Only**: Only used in WAV files (not MP3 or FLAC)
- ❌ **Limited Fields**: Fewer standardized fields than ID3v2
- ❌ **No Multiple Values**: Single value per field (though some use separators)
- ❌ **No Binary Data**: Cannot embed images directly
- ❌ **Less Common**: Not as widely used as ID3v2
- ❌ **Implementation Varies**: Different tools handle fields differently

### Use Cases

- **WAV Files**: Standard metadata format for WAV files
- **Professional Audio**: Used in professional audio production
- **Broadcasting**: Compatible with Broadcast Wave Format (BWF)
- **Simple Metadata**: When basic metadata is sufficient
- **Native Format**: When you want to use WAV's native metadata system

### Specifications

- **RIFF Specification**: [RIFF File Format](https://www.loc.gov/preservation/digital/formats/fdd/fdd000025.shtml)
- **WAV Specification**: [WAV File Format](https://www.loc.gov/preservation/digital/formats/fdd/fdd000001.shtml)
- **INFO Chunk**: [RIFF INFO Chunk Specification](https://en.wikipedia.org/wiki/Resource_Interchange_File_Format)

### AudioMeta Support

- **Read/Write**: Full support
- **File Types**: WAV (native)
- **Implementation**: Custom implementation (mutagen doesn't support writing RIFF)
- **BWF Support**: Raw extraction implemented (bext chunk reading)
  - **BWF Versions**: Supports reading v0, v1, and v2 bext chunks
  - **Fields Extracted**: Description, Originator, OriginatorReference, OriginationDate, OriginationTime, TimeReference, Version, UMID, CodingHistory
  - **Loudness Metadata**: Not yet parsed (v2 loudness fields are in reserved space)
  - **Writing**: Planned but not yet implemented
    - When implemented, writing `bext` metadata to a WAV file without a `bext` chunk will automatically create/add the `bext` chunk, converting the file to BWF format

---

## Format Comparison

| Feature                | ID3v1          | ID3v2          | Vorbis        | RIFF            |
| ---------------------- | -------------- | -------------- | ------------- | --------------- |
| **Introduced**         | 1996           | 1998-2000      | 2000          | 1991            |
| **File Types**         | MP3, FLAC, WAV | MP3, WAV, FLAC | FLAC          | WAV             |
| **Text Encoding**      | ASCII          | UTF-16/UTF-8   | UTF-8         | ASCII/UTF-8     |
| **Max Text Length**    | 30 chars       | ~8MB           | ~8MB          | ~1MB            |
| **Multiple Values**    | ❌             | ✅             | ✅            | ⚠️ (separators) |
| **Unicode Support**    | ❌             | ✅             | ✅            | ✅              |
| **Cover Art**          | ❌             | ✅             | ⚠️ (separate) | ❌              |
| **Custom Fields**      | ❌             | ✅             | ✅            | ⚠️              |
| **Complexity**         | Simple         | Complex        | Simple        | Medium          |
| **Compatibility**      | Excellent      | Good           | Good          | Good            |
| **File Size Overhead** | 128 bytes      | Variable (KB)  | Variable (KB) | Variable (KB)   |

### When to Use Each Format

**Use ID3v1 when:**

- Maximum compatibility is required
- Working with very old hardware/software
- File size overhead must be minimal
- Only basic metadata is needed

**Use ID3v2 when:**

- Working with MP3 files
- Need extensive metadata (BPM, rating, lyrics, etc.)
- Need multiple artists/genres
- Need cover art
- Working across MP3, WAV, and FLAC

**Use Vorbis when:**

- Working with FLAC files
- Prefer simple, readable metadata
- Need multiple values natively
- Working in open-source ecosystems

**Use RIFF when:**

- Working with WAV files
- Want native WAV metadata format
- Professional audio production
- Broadcasting applications (with BWF)

---

## AudioMeta Implementation

### Format Detection

AudioMeta automatically detects available metadata formats in files:

- **MP3**: Checks for ID3v2 (beginning) and ID3v1 (end)
- **FLAC**: Checks for Vorbis comments, ID3v2, and ID3v1
- **WAV**: Checks for RIFF INFO, ID3v2, and ID3v1

### Reading Priority

When multiple formats are present, AudioMeta uses priority order:

- **MP3**: ID3v2 → ID3v1
- **FLAC**: Vorbis → ID3v2 → ID3v1
- **WAV**: RIFF → ID3v2 → ID3v1

### Writing Strategy

AudioMeta supports three writing strategies:

1. **SYNC** (default): Write to native format, sync to other present formats
2. **PRESERVE**: Write to native format, preserve other formats unchanged
3. **CLEANUP**: Write to native format, remove other formats

### Format-Specific Handling

- **ID3v1**: Direct file manipulation, 30-char truncation, genre code mapping
- **ID3v2**: Mutagen library, version selection (v2.3 default), frame handling
- **Vorbis**: Mutagen library with custom parsing, case-insensitive keys
- **RIFF**: Custom implementation, FourCC handling, chunk structure management

### Unified API

AudioMeta provides a unified API that abstracts format differences:

- **Single Function**: `get_unified_metadata()` works with all formats
- **Field Normalization**: Field names normalized across formats
- **Value Conversion**: Automatic conversion (e.g., genre codes to names)
- **Multiple Values**: Intelligent handling of multiple values per format

For detailed information on field support and handling, see the **[Metadata Field Guide](METADATA_FIELD_GUIDE.md)**.
