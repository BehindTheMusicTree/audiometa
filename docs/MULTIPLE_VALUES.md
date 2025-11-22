# Multiple Values Handling

The library intelligently handles multiple values across different metadata formats, automatically choosing the best approach for each situation.

## Semantic Classification

Fields are classified based on their intended use:

- **Semantically Multi-Value Fields**: Fields that can logically contain multiple values (e.g., `ARTISTS`, `GENRES_NAMES`). They can be stored as multiple entries or concatenated values.
- **Semantically Single-Value Fields**: Fields that are intended to hold a single value (e.g., `TITLE`, `ALBUM`). They are typically stored as a single entry but some formats may allow multiple entries.

## Semantically Single-Value Fields

The library always returns only the first value for these fields, regardless of how many values are present in the metadata.

## Semantically Multi-Value Fields

The library can handle multiple values for these fields.

### List of Semantically Multi-Value Fields

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

## Ways to Handle Multiple Values

Metadata formats can represent multi-value fields in two ways:

### Multiple Field Instances (Multi-Frame/Multi-Key)

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

### Single Field with Separated Values (Separator-Based)

All values are stored in one field, separated by a character or delimiter.

Example:

```
ARTIST=Artist 1; Artist 2
```

- Used when repeated fields aren't officially supported, though repeated fields could still occur in these formats.
- In ID3v2.4, the official separator is a null byte (\\0).

| Format  | Separator(s)   | Notes                                                       |
| ------- | -------------- | ----------------------------------------------------------- |
| ID3v1   | `/`, `;`, `,`  | Single field only; multi-values concatenated with separator |
| ID3v2.3 | `/`, `;`       | Uses single frame with separators                           |
| ID3v2.4 | `/`, `;`, `\0` | Null-separated values preferred;                            |
| RIFF    | `/`, `;`       | Not standardized; concatenation varies by implementation    |
| Vorbis  | rare, `\0`     | Native repeated fields make, sometimes null-separated       |

## Reading Semantically Multiple Values

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

### Smart Separator Parsing of Concatenated Values

When parsing concatenated values from a single instance, the library uses an intelligent separator detection mechanism:

1. `//` (double slash)
2. `\\` (double backslash)
3. `;` (semicolon)
4. `\` (backslash)
5. `/` (forward slash)
6. `,` (comma)

### Detailed Examples of Smart Semantically Multi-Value Logic

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

## Writing Semantically Multiple Values

### Strategy Overview

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

### Writing Duplicate Values

When writing duplicate values, the library won't preserve them.

```python
from audiometa import update_metadata

update_metadata("song.wav", {"artists": ["Artist One", "Artist Two", "Artist One", "Artist Three", "Artist Two"]})
# Result: "Artist One;Artist Two;Artist Three"
```

### Automatic Empty Value Filtering

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

### Smart Separator Selection

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

### Examples of Smart Separator Selection

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
