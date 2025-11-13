# Genre Handling

AudioMeta provides comprehensive genre support across all audio formats, with intelligent handling of genre codes, multiple genres, and format-specific limitations.

## Genre Support by Format

### Genre Support Matrix

| Format      | Multiple | Id3v1 Codes | Code + Text | Custom Text |
| ----------- | -------- | ----------- | ----------- | ----------- |
| **ID3v1**   | ❌       | ✅          | ❌          | ❌          |
| **ID3v2.3** | ✅       | ✅          | ✅          | ✓           |
| **ID3v2.4** | ✅       | ✓           | ✓           | ✅          |
| **Vorbis**  | ✅       | ❌          | ❌          | ✅          |
| **RIFF**    | ✓        | ✓           | ✓           | ✅          |

### ID3v1 Genre Support

ID3v1 provides the most limited genre support with a fixed set of predefined genres.

**Genre Storage:**

- **Format**: Single byte numeric code (0-255)
- **Multiple Genres**: Not supported - only one genre per file
- **Custom Genres**: Not supported - must use predefined codes
- **Code Range**: 0-147 standard, 148-191 Winamp extensions, 192-255 unused

**Examples:**

- Code `17` → "Rock"
- Code `255` → Unknown/unspecified genre

### ID3v2.3 Genre Support

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

### ID3v2.4 Genre Support

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

### Vorbis Genre Support

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

### RIFF Genre Support

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

## ID3v1 Genre Code System

ID3v1 uses a standardized genre code system (also used by RIFF) with 192 predefined genres:

- **Genres 0-79**: Original ID3v1 specification
- **Genres 80-125**: Winamp extensions
- **Genres 126-147**: Other players' extensions
- **Genres 148-191**: Winamp 5.6 extensions (November 2010)
- **Code 255**: Unknown/unspecified genre

An exhaustive list of all genre codes is available [here](../audiometa/utils/id3v1_genre_code_map.py).

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

## Reading and Writing Strategy

### Reading Genres

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

### Writing Genres

When writing genres, AudioMeta uses a smart strategy based on the target format's capabilities:

#### Writing Genres for ID3v1

- Selects the first genre from the provided list and converts it to the corresponding ID3v1 code
- If no matching code is found, sets genre to `255` (unknown)

#### Writing Genres for ID3v2.3

- If all genres have corresponding ID3v1 codes, uses parentheses notation (with text if available)
- If any genre lacks a code, uses separator-based text format with smart separator selection

#### Writing Genres for ID3v2.4

- Writes all genres as null-separated text values

#### Writing Genres for Vorbis

- Writes each genre name as a separate GENRE entry

#### Writing Genres for RIFF

- Writes genres as text using smart separator selection
