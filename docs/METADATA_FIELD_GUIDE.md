# Metadata Field Guide: Support and Handling

This document consolidates comprehensive metadata field handling across all supported audio formats (ID3v1, ID3v2, Vorbis, RIFF). It merges documentation on multiple values, genre handling, rating handling, track number handling, release date validation rules, and lyrics support into a single authoritative reference.

## Table of Contents

- [Metadata Support by Format](#metadata-support-by-format)
- [Multiple Values Handling](#multiple-values-handling)
- [Genre Handling](#genre-handling)
- [Rating Handling](#rating-handling)
- [Release Date Validation Rules](#release-date-validation-rules)
- [Track Number Handling](#track-number-handling)
- [Lyrics Support](#lyrics-support)
- [None vs Empty String Handling](#none-vs-empty-string-handling)

## Metadata Support by Format

The library supports a comprehensive set of metadata fields across different audio formats. The table below shows which fields are supported by each format:

| Field               | ID3v1             | ID3v2                      | Vorbis               | RIFF            | AudioMeta Support     |
| ------------------- | ----------------- | -------------------------- | -------------------- | --------------- | --------------------- |
| Text Encoding       | ASCII             | UTF-16/ISO (v2.3)          | UTF-8                | ASCII/UTF-8     | UTF-8                 |
|                     |                   | + UTF-8 (v2.4)             |                      |                 |                       |
| Max Text Length     | 30 chars          | ~8M chars                  | ~8M chars            | ~1M chars       | Format limit          |
| Date Time Formats   | YYYY              | YYYY+DDMM (v2.3)           | YYYY-MM-DD           | YYYY-MM-DD      | ISO 8601              |
|                     |                   | YYYY-MM-DD (v2.4)          |                      |                 |                       |
| Technical Info      |                   |                            |                      |                 |                       |
| - Duration          | ✓                 | ✓                          | ✓                    | ✓               | ✓                     |
| - Bitrate           | ✓                 | ✓                          | ✓                    | ✓               | ✓                     |
| - Sample Rate       | ✓                 | ✓                          | ✓                    | ✓               | ✓                     |
| - Channels          | ✓ (1-2)           | ✓ (1-255)                  | ✓ (1-255)            | ✓ (1-2)         | ✓                     |
| - File Size         | ✓                 | ✓                          | ✓                    | ✓               | ✓                     |
| - Format Info       | ✓                 | ✓                          | ✓                    | ✓               | ✓                     |
| - MD5 Checksum      |                   |                            | ✓                    |                 | ✓ (FLAC)              |
| Title               | TITLE (30)        | TIT2                       | TITLE                | INAM            | TITLE                 |
| Artists             | ARTIST (30)       | TPE1                       | ARTIST               | IART            | ARTISTS (list)        |
| Album               | ALBUM (30)        | TALB                       | ALBUM                | IPRD            | ALBUM                 |
| Album Artists       | ✗                 | TPE2                       | ALBUMARTIST          | IAAR\*          | ALBUM_ARTISTS (list)  |
| Genres              | GENRE (1#)        | TCON                       | GENRE                | IGNR            | GENRES_NAMES (list)   |
| Release Date        | YEAR (4)          | TYER (4) + TDAT (4) (v2.3) | DATE (10)            | ICRD (10)       | RELEASE_DATE          |
|                     |                   | TDRC (10) (v2.4)           |                      |                 |                       |
| Track Number        | TRACK (1#) (v1.1) | TRCK (0-255#)              | TRACKNUMBER (Unlim#) | IPRT\* (Unlim#) | TRACK_NUMBER          |
| Disc Number         | ✗                 | TPOS (0-255#)              | DISCNUMBER (Unlim#)  | ✗               |                       |
| Rating              | ✗                 | POPM (0-255#)              | RATING (0-100#)      | IRTD\* (0-100#) | RATING                |
| BPM                 | ✗                 | TBPM (0-65535#)            | BPM (0-65535#)       | IBPM\*          | BPM                   |
| Language            | ✗                 | TLAN (3)                   | LANGUAGE (3)         | ILNG\* (3)      | LANGUAGE              |
| Composers           | ✗                 | TCOM                       | COMPOSER             | ICMP            | COMPOSERS (list)      |
| Publisher           | ✗                 | TPUB                       | ORGANIZATION         | ✗               | PUBLISHER             |
| Copyright           | ✗                 | TCOP                       | COPYRIGHT            | ICOP            | COPYRIGHT             |
| Lyrics              | ✗                 | USLT                       | LYRICS\*             | ✗               | UNSYNCHRONIZED_LYRICS |
| Synchronized Lyrics | ✗                 | SYLT                       | ✗                    | ✗               |                       |
| Comment             | COMMENT (28)      | COMM                       | COMMENT              | ICMT            | COMMENT               |

## Multiple Values Handling

The library intelligently handles multiple values across different metadata formats, automatically choosing the best approach for each situation.

### Semantic Classification

Fields are classified based on their intended use:

- **Semantically Multi-Value Fields**: Fields that can logically contain multiple values (e.g., `ARTISTS`, `GENRES_NAMES`). They can be stored as multiple entries or concatenated values.
- **Semantically Single-Value Fields**: Fields that are intended to hold a single value (e.g., `TITLE`, `ALBUM`). The library always returns only the first value for these fields.

### Semantically Multi-Value Fields

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

### Ways to Handle Multiple Values

Metadata formats can represent multi-value fields in two ways:

#### Multiple Field Instances (Multi-Frame/Multi-Key)

Each value is stored as a separate instance of the same field or frame. Vorbis comments natively support this; ID3v2 and RIFF may contain multiple instances. ID3v1 does not.

#### Single Field with Separated Values (Separator-Based)

All values are stored in one field, separated by a character or delimiter (e.g., `;`, `/`, `,`, or a null byte for ID3v2.4).

### Reading Semantically Multiple Values

AudioMeta follows a two-step process:

1. Extract all field instances as found in the file for each format.
2. If null-separator (ID3v2.4) is present, split on null bytes. Otherwise:
   - If multiple instances exist: return them as-is.
   - If a single instance exists: apply smart separator parsing using a priority list: `//`, `\\`, `;`, `\`, `/`, `,`.

### Writing Semantically Multiple Values

Writing adapts to format capabilities:

| Format  | Multi-value Writing Method                     |
| ------- | ---------------------------------------------- |
| ID3v1   | Concatenated with chosen single-char separator |
| ID3v2.3 | Separator-based concatenation                  |
| ID3v2.4 | Null-separated values                          |
| RIFF    | Separator-based concatenation                  |
| Vorbis  | Multiple entries (one per value)               |

Duplicate values are de-duplicated before writing. Empty strings and `None` values are filtered out; if all values are removed, the field is deleted.

### Automatic Empty Value Filtering

The library automatically filters out empty strings and `None` values from list-type metadata fields before writing. If all values in a list are filtered out, the field is removed entirely (set to `None`).

## Genre Handling

AudioMeta provides comprehensive genre support across all audio formats, with intelligent handling of genre codes, multiple genres, and format-specific limitations.

### Genre Support by Format

| Format  | Multiple | ID3v1 Codes | Custom Text |
| ------- | -------- | ----------- | ----------- |
| ID3v1   | ❌       | ✅          | ❌          |
| ID3v2.3 | ✅       | ✅          | ✓           |
| ID3v2.4 | ✅       | ✓           | ✅          |
| Vorbis  | ✅       | ❌          | ✅          |
| RIFF    | ✓        | ✓           | ✅          |

### ID3v1 Genre Support

ID3v1 provides the most limited genre support with a fixed set of predefined genres (0-147 standard, 148-191 Winamp extensions, 192-255 unused).

- **Format**: Single byte numeric code (0-255)
- **Multiple Genres**: Not supported - only one genre per file
- **Custom Genres**: Not supported - must use predefined codes
- **Examples**: Code `17` → "Rock", Code `255` → Unknown/unspecified genre

### ID3v2.3 Genre Support

Uses the TCON (Content type) frame with support for numeric codes and text.

- **Format**: Numeric string with optional parentheses notation
- **Multiple Genres**: Supported via consecutive parentheses (e.g., `"(51)(39)"`) or with text
- **Custom Genres**: Not officially supported, but widely used
- **Examples**: `"(17)"` → Rock, `"(51)(39)"` → Trance + Cover, `"Rock/Blues"` → Multiple text genres

### ID3v2.4 Genre Support

Provides the most flexible genre support among ID3v2 versions.

- **Format**: UTF-8 encoded text with null-byte separation for multiple values
- **Multiple Genres**: Full support using null-separated values
- **Custom Genres**: Unlimited custom genre names
- **Examples**: `"Rock"` → Direct text genre, `"Rock\0Blues"` → Multiple text genres

### Vorbis Genre Support

Text-based genres using multiple `GENRE` entries; unlimited custom names.

- **Format**: UTF-8 text comments
- **Multiple Genres**: Multiple GENRE fields (official) or separators (unofficial)

### RIFF Genre Support

Supports both numeric codes and text genres.

- **Format**: IGNR chunk containing either text (official) or numeric code (unofficial)
- **Multiple Genres**: Limited - typically single value, but text mode can use separators

### Reading and Writing Strategy

When reading, AudioMeta extracts all genre entries, applies separator parsing when only a single entry is present, converts numeric codes using the ID3v1 code map, and returns a unique list of names.

When writing, behavior depends on the target format (ID3v1 picks the closest code or `255` for unknown; ID3v2.4 writes null-separated text; Vorbis writes multiple GENRE entries; RIFF uses smart separators).

## Rating Handling

AudioMeta implements a sophisticated rating profile system to handle the complex compatibility requirements across different audio players and formats.

### The Rating Profile Problem

Different audio players use completely different numeric values for the same star ratings. For example, a 3-star rating can be stored as:

- `128` (Windows Media Player, MusicBee, Winamp)
- `60` (FLAC players, Vorbis)
- `153` (Traktor)

### Rating Profile Types

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
- **Half-star support**: ❌ No support (only whole stars: 1, 2, 3, 4, 5)

### Rating Normalization

AudioMeta supports two modes for handling ratings:

1. **Raw Mode** (default): Returns and accepts raw profile-specific values
2. **Normalized Mode**: Converts between raw values and a normalized scale

```python
from audiometa import get_unified_metadata, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey

# Reading without normalization (raw values)
metadata = get_unified_metadata("song.mp3")
rating = metadata.get(UnifiedMetadataKey.RATING)  # Returns: 128, 60, 153, etc. (raw profile values)

# Reading with normalization
metadata = get_unified_metadata("song.mp3", normalized_rating_max_value=10)
rating = metadata.get(UnifiedMetadataKey.RATING)  # Returns: 0, 2, 4, 6, 8, 10 (normalized)

# Writing without normalization (raw values)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 128})  # Direct raw value

# Writing with normalization
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 6}, normalized_rating_max_value=10)  # Writes 128 (Profile A)
update_metadata("song.flac", {UnifiedMetadataKey.RATING: 6}, normalized_rating_max_value=10)  # Writes 60 (Profile B)
```

### Normalized Rating Scale

When `normalized_rating_max_value` is provided, AudioMeta uses a normalized scale. With `normalized_rating_max_value=10`, the scale is:

```
0 = No rating
2 = 1 star
4 = 2 stars
6 = 3 stars
8 = 4 stars
10 = 5 stars
```

### Rating Validation Rules

When `normalized_rating_max_value` is not provided (raw mode), any non-negative integer is allowed.

When `normalized_rating_max_value` is provided (normalized mode), the rating value must map to a valid profile value. Invalid rating values raise `InvalidRatingValueError`.

## Release Date Validation Rules

The `RELEASE_DATE` field accepts two formats:

**Valid Formats:**

1. **YYYY format** (4 digits) - for year-only dates
   - Examples: `"2024"`, `"1900"`, `"1970"`, `"0000"`, `"9999"`
   - Use when you only know the year

2. **YYYY-MM-DD format** (ISO-like format) - for full dates
   - Examples: `"2024-01-01"`, `"2024-12-31"`, `"1900-01-01"`, `"1970-06-15"`
   - Month and day must be zero-padded (2 digits each)
   - Use when you have the complete date

3. **Empty string** - allowed and represents no date
   - Example: `""`

**Invalid Formats:**

The following formats will raise `InvalidMetadataFieldFormatError`:

- Wrong separator: `"2024/01/01"`, `"2024.01.01"`, `"2024_01_01"`, `"2024 01 01"`
- Incomplete date: `"2024-1-1"`, `"2024-1-01"`, `"2024-01-1"`
- Short year: `"24"`, `"202"`, `"20"`
- Long year: `"20245"`, `"20245-01-01"`
- Non-numeric: `"not-a-date"`, `"2024-abc-01"`, `"abcd-01-01"`
- Incomplete format: `"2024-01"`, `"2024-"`, `"-01-01"`, `"2024-01-"`

**Examples:**

```python
from audiometa import update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey

# Valid: YYYY format
update_metadata("song.mp3", {UnifiedMetadataKey.RELEASE_DATE: "2024"})

# Valid: YYYY-MM-DD format
update_metadata("song.mp3", {UnifiedMetadataKey.RELEASE_DATE: "2024-01-01"})

# Valid: empty string
update_metadata("song.mp3", {UnifiedMetadataKey.RELEASE_DATE: ""})

# Invalid: wrong separator
update_metadata("song.mp3", {UnifiedMetadataKey.RELEASE_DATE: "2024/01/01"})
# Raises: InvalidMetadataFieldFormatError
```

## Track Number Handling

The library handles different track number formats across audio metadata standards.

### Track Number Formats by Format

- **ID3v1**: Simple numeric string (stored in comment field since ID3v1.1), e.g., `"5"`, `"12"`
- **ID3v2**: Supports `"track/total"` format (e.g., `"5/12"`, `"99/99"`) or simple `"track"` format (e.g., `"5"`)
- **Vorbis**: Simple numeric string (or `track/total` where used), e.g., `"5"`, `"12"`
- **RIFF**: Simple numeric string, e.g., `"5"`, `"12"`

### Reading Track Number

The library returns track numbers as strings. Edge cases:

- `"5/"` → Track number: `"5/"` (trailing slash preserved)
- `"/12"` → Track number: `None` (no track number before slash)
- `"abc/def"` → Track number: `None` (non-numeric values)
- `""` → Track number: `None` (empty string)
- `"5/12/15"` → Track number: `None` (multiple slashes, invalid format)
- `"5-12"` → Track number: `"5-12"` (different separator preserved)
- `"01"` → Track number: `"01"` (leading zeros preserved)

### Writing Track Number

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

## Lyrics Support

Two types of lyrics are supported: synchronized lyrics (synchronized with music, for karaoke) and unsynchronized lyrics (plain text).

### Synchronized Lyrics

Synchronized lyrics (SYLT frames in ID3v2) are not currently supported by the library. This is planned for future versions.

### Unsynchronized Lyrics

Unsynchronized lyrics are supported differently across formats:

#### ID3v1 Unsynchronized Lyrics

ID3v1 does not support unsynchronized lyrics due to its limited structure.

#### ID3v2 Unsynchronized Lyrics

ID3v2 supports unsynchronized lyrics through the `USLT` (Unsynchronized Lyrics/Text transcription) frame. The library currently writes only a single `USLT` frame with default language code `eng`. Multi-language support is planned for future versions.

#### RIFF Unsynchronized Lyrics

RIFF INFO chunks support storing unsynchronized lyrics in the `UNSYNCHRONIZED_LYRICS` chunk. Language codes are not supported due to lack of standardization.

#### Vorbis Unsynchronized Lyrics

Vorbis comments support lyrics through the `UNSYNCHRONIZED_LYRICS` field. Language codes are not supported due to lack of standardization.

## None vs Empty String Handling

The library handles `None` and empty string values differently across audio formats:

| Format            | Setting to `None`        | Setting to `""` (empty string)   | Read Back Result               |
| ----------------- | ------------------------ | -------------------------------- | ------------------------------ |
| **ID3v2 (MP3)**   | Removes field completely | Removes field completely         | `None` / `None`                |
| **Vorbis (FLAC)** | Removes field completely | Creates field with empty content | `None` / `""`                  |
| **RIFF (WAV)**    | Removes field completely | Removes field completely         | `None` / `None`                |
| **ID3v1 (MP3)**   | ✅ **Supported**         | ✅ **Supported**                 | Legacy format with limitations |

### Example

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
