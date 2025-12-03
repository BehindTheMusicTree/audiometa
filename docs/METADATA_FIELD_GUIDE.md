# Metadata Field Guide: Support and Handling

This document consolidates comprehensive metadata field handling across all supported audio formats (ID3v1, ID3v2, Vorbis, RIFF). It merges documentation on multiple values, genre handling, rating handling, track number handling, release date validation rules, and lyrics support into a single authoritative reference.

**Note**: For detailed information about each metadata format (history, structure, advantages, disadvantages), see the **[Metadata Formats Guide](METADATA_FORMATS.md)**.

**Note**: For audio information (duration, bitrate, sample rate, channels, file size, format info, MD5 checksum), see the **[Audio Technical Info Guide](AUDIO_TECHNICAL_INFO_GUIDE.md)**.

## Table of Contents

- [Metadata Support by Format](#metadata-support-by-format)
- [Multiple Values Handling](#multiple-values-handling)
- [Genre Handling](#genre-handling)
- [Rating Handling](#rating-handling)
- [Release Date Validation Rules](#release-date-validation-rules)
- [ISRC Validation Rules](#isrc-validation-rules)
- [Track Number Handling](#track-number-handling)
- [Disc Number Handling](#disc-number-handling)
- [Lyrics Support](#lyrics-support)
- [None vs Empty String Handling](#none-vs-empty-string-handling)

## Metadata Support by Format

The library supports a comprehensive set of metadata fields across different audio formats. The table below shows which fields are supported by each format:

| Field                   | ID3v1             | ID3v2                      | Vorbis            | RIFF                          | AudioMeta             | CLI                      |
| ----------------------- | ----------------- | -------------------------- | ----------------- | ----------------------------- | --------------------- | ------------------------ |
| Text Encoding           | ASCII             | UTF-16/ISO (v2.3)          | UTF-8             | ASCII/UTF-8                   | UTF-8                 | ✗                        |
|                         |                   | + UTF-8 (v2.4)             |                   |                               |                       |                          |
| Max Text Length         | 30 chars          | ~8M chars                  | ~8M chars         | ~1M chars                     | Format limit          | ✗                        |
| Date Time Formats       | YYYY              | YYYY+DDMM (v2.3)           | YYYY-MM-DD        | YYYY-MM-DD                    | ISO 8601              | ✗                        |
|                         |                   | YYYY-MM-DD (v2.4)          |                   |                               |                       |                          |
| Title                   | TITLE (30)        | TIT2                       | TITLE             | INAM                          | TITLE                 | --title                  |
| Artists                 | ARTIST (30)       | TPE1                       | ARTIST            | IART                          | ARTISTS               | --artist, multiple       |
| Album                   | ALBUM (30)        | TALB                       | ALBUM             | IPRD                          | ALBUM                 | --album                  |
| Album Artists           | ✗                 | TPE2                       | ALBUMARTIST       | IAAR\*                        | ALBUM_ARTISTS         | --album-artist, multiple |
| Genres                  | GENRE (1#)        | TCON                       | GENRE             | IGNR                          | GENRES_NAMES          | --genre, multiple        |
| Release Date            | YEAR (4)          | TYER (4) + TDAT (4) (v2.3) | DATE (10)         | ICRD (10)                     | RELEASE_DATE          | --year or --release-date |
|                         |                   | TDRC (10) (v2.4)           |                   |                               |                       |                          |
| Track Number            | TRACK (1#) (v1.1) | TRCK (0-255#)              | TRACKNUMBER       | IPRT\*                        | TRACK_NUMBER          | --track-number           |
| Disc Number             | ✗                 | TPOS (0-255#)              | DISCNUMBER        | ✗                             | DISC_NUMBER           | --disc-number            |
| Disc Total              | ✗                 | TPOS (0-255#)              | DISCTOTAL         | ✗                             | DISC_TOTAL            | --disc-total             |
| Rating                  | ✗                 | POPM (0-255#)              | RATING (0-100#)   | IRTD\* (0-100#)               | RATING                | --rating                 |
| BPM                     | ✗                 | TBPM (0-65535#)            | BPM (0-65535#)    | IBPM\*                        | BPM                   | --bpm                    |
| Language                | ✗                 | TLAN (3)                   | LANGUAGE (3)      | ILNG\* (3)                    | LANGUAGE              | --language               |
| Composers               | ✗                 | TCOM                       | COMPOSER          | ICMP                          | COMPOSERS             | --composer, multiple     |
| Publisher               | ✗                 | TPUB                       | ORGANIZATION      | ✗                             | PUBLISHER             | --publisher              |
| Copyright               | ✗                 | TCOP                       | COPYRIGHT         | ICOP                          | COPYRIGHT             | --copyright              |
| Lyrics                  | ✗                 | USLT                       | LYRICS\*          | ✗                             | UNSYNCHRONIZED_LYRICS | --lyrics                 |
| Synchronized Lyrics     | ✗                 | SYLT                       | ✗                 | ✗                             |                       | ✗                        |
| Comment                 | COMMENT (28)      | COMM                       | COMMENT           | ICMT                          | COMMENT               | --comment                |
| ReplayGain              | ✗                 | ✗                          | REPLAYGAIN        | ✗                             | REPLAYGAIN            | --replaygain             |
| Archival Location       | ✗                 | TXXX                       | ARCHIVAL_LOCATION | ✗                             | ARCHIVAL_LOCATION     | --archival-location      |
| ISRC                    | ✗                 | TSRC                       | ISRC              | \*\* (ISRC)                   | ISRC                  | --isrc                   |
| Description             | ✗                 | ✗                          | ✗                 | \*\* (Description)            |                       | ✗                        |
| Originator              | ✗                 | ✗                          | ✗                 | \*\* (Originator)             |                       | ✗                        |
| Originator Reference    | ✗                 | ✗                          | ✗                 | \*\* (OriginatorReference)    |                       | ✗                        |
| Origination Date        | ✗                 | ✗                          | ✗                 | \*\* (OriginationDate)        |                       | ✗                        |
| Origination Time        | ✗                 | ✗                          | ✗                 | \*\* (OriginationTime)        |                       | ✗                        |
| Time Reference          | ✗                 | ✗                          | ✗                 | \*\* (TimeReference)          |                       | ✗                        |
| Version                 | ✗                 | ✗                          | ✗                 | \*\* (Version)                |                       | ✗                        |
| UMID                    | ✗                 | ✗                          | ✗                 | \*\* (UMID)                   |                       | ✗                        |
| Coding History          | ✗                 | ✗                          | ✗                 | \*\* (CodingHistory)          |                       | ✗                        |
| Loudness Value          | ✗                 | ✗                          | ✗                 | \*\*\* (LoudnessValue)        |                       | ✗                        |
| Loudness Range          | ✗                 | ✗                          | ✗                 | \*\*\* (LoudnessRange)        |                       | ✗                        |
| Max True Peak Level     | ✗                 | ✗                          | ✗                 | \*\*\* (MaxTruePeakLevel)     |                       | ✗                        |
| Max Momentary Loudness  | ✗                 | ✗                          | ✗                 | \*\*\* (MaxMomentaryLoudness) |                       | ✗                        |
| Max Short Term Loudness | ✗                 | ✗                          | ✗                 | \*\*\* (MaxShortTermLoudness) |                       | ✗                        |

\* Fields marked with asterisk (\*) are supported via RIFF INFO chunks but may have limited or non-standard implementations.

\*\* Fields marked with double asterisk (\*\*) are Broadcast Wave Format (BWF) fields via the `bext` chunk. Currently only ISRC is exposed in unified metadata. Other BWF fields are available via raw metadata access. See the [Metadata Formats Guide](METADATA_FORMATS.md#broadcast-wave-format-bwf-versions) for details.

\*\*\* Fields marked with triple asterisk (\*\*\*) are Broadcast Wave Format (BWF) v2 loudness metadata fields via the `bext` chunk. These fields are currently available via raw metadata access only, not through unified metadata. See the [Metadata Formats Guide](METADATA_FORMATS.md#broadcast-wave-format-bwf-versions) for details.

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

AudioMeta provides comprehensive genre support across all audio formats, with intelligent handling of genre codes, multiple genres, and format-specific limitations. See the **[Genre Handling Guide](GENRE_HANDLING.md)**.

## Rating Handling

Rating is supported across multiple audio formats, with normalization in unified metadata. See the **[Rating Handling Guide](RATING_HANDLING.md)**.

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

## ISRC Validation Rules

The `ISRC` (International Standard Recording Code) field accepts two formats based on ISO 3901:

**Valid Formats:**

1. **12 alphanumeric characters** (without hyphens) - compact format

   - Format: `CCXXXYYNNNNN`
   - Examples: `"USRC17607839"`, `"GBAYE0000001"`, `"JPAB01234567"`
   - CC = Country code (2 letters)
   - XXX = Registrant code (3 alphanumeric)
   - YY = Year of reference (2 digits)
   - NNNNN = Unique designation code (5 digits)

2. **15 characters with hyphens** - human-readable format

   - Format: `CC-XXX-YY-NNNNN`
   - Examples: `"US-RC1-76-07839"`, `"GB-AYE-00-00001"`, `"JP-AB0-12-34567"`

3. **Empty string** - allowed and represents no ISRC
   - Example: `""`

**Invalid Formats:**

The following formats will raise `InvalidMetadataFieldFormatError`:

- Too short: `"USRC1760783"`, `"ABC"`, `"U"`
- Too long: `"USRC176078390"`, `"USRC1760783901234"`
- Wrong hyphen positions: `"USRC-17607839"`, `"US-RC17607839"`
- Special characters: `"USRC1760783!"`, `"USRC@7607839"`, `"USRC 7607839"`
- Wrong segment lengths in hyphenated format: `"US-R-76-07839"`, `"USA-RC1-76-07839"`

**Examples:**

```python
from audiometa import update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey

# Valid: 12-character format
update_metadata("song.mp3", {UnifiedMetadataKey.ISRC: "USRC17607839"})

# Valid: hyphenated format
update_metadata("song.mp3", {UnifiedMetadataKey.ISRC: "US-RC1-76-07839"})

# Valid: empty string
update_metadata("song.mp3", {UnifiedMetadataKey.ISRC: ""})

# Invalid: too short
update_metadata("song.mp3", {UnifiedMetadataKey.ISRC: "ABC"})
# Raises: InvalidMetadataFieldFormatError
```

**Format Support:**

| Format | ISRC Support |
| ------ | ------------ |
| ID3v1  | ❌           |
| ID3v2  | ✅ (TSRC)    |
| Vorbis | ✅ (ISRC)    |
| RIFF   | ✅ (ISRC)    |

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

For detailed information, see the **[Track Number Handling Guide](TRACK_NUMBER.md)**.

## Disc Number Handling

The library provides two separate unified metadata fields for disc number:

- **`DISC_NUMBER`**: Integer representing the current disc number (required)
- **`DISC_TOTAL`**: Integer representing the total number of discs, or `None` if unknown (optional)

**Format Support:**

- **ID3v1**: ✗ Not supported (format limitation)
- **ID3v2**: TPOS frame - maps `"disc/total"` format to/from `DISC_NUMBER` and `DISC_TOTAL`, limited to 0-255 range
- **Vorbis**: Native separate `DISCNUMBER` and `DISCTOTAL` fields, unlimited range
- **RIFF**: ✗ Not supported (format limitation)

For detailed information on disc number formats, limitations, reading/writing behavior, and examples, see the **[Disc Number Handling Guide](DISC_NUMBER.md)**.

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
