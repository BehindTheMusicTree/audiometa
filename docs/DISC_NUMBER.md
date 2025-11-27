# Disc Number Handling

The library handles different disc number formats across audio metadata standards:

## ID3v1 Disc Number Format

ID3v1 does not support disc numbers due to its limited fixed structure.

- **Support**: ✗ Not supported
- **Reason**: ID3v1 has a fixed 128-byte structure with no field for disc number
- **Workaround**: None available (format limitation)

## ID3v2 Disc Number Format

ID3v2 supports disc numbers through the `TPOS` (Part of a set) frame.

- **Frame**: TPOS (Part of a set)
- **Format**: `"disc/total"` (e.g., `"1/2"`, `"2/3"`, `"99/99"`) or simple `"disc"` (e.g., `"1"`, `"2"`)
- **Range**: 0-255 for both disc number and total discs
- **Unified API Mapping**:
  - `TPOS="1/2"` → `DISC_NUMBER=1`, `DISC_TOTAL=2`
  - `TPOS="1"` → `DISC_NUMBER=1`, `DISC_TOTAL=None`
- **Examples**:
  - `"1/2"` → `DISC_NUMBER=1`, `DISC_TOTAL=2` (disc 1 of 2)
  - `"2/3"` → `DISC_NUMBER=2`, `DISC_TOTAL=3` (disc 2 of 3)
  - `"1"` → `DISC_NUMBER=1`, `DISC_TOTAL=None` (simple format, disc 1, total unknown)
  - `"99/99"` → `DISC_NUMBER=99`, `DISC_TOTAL=99` (maximum supported value)

**Limitations:**

- Maximum disc number: 255
- Maximum total discs: 255
- Values exceeding 255 are typically truncated or may cause errors depending on the implementation

## Vorbis Disc Number Format

Vorbis comments support disc numbers through separate `DISCNUMBER` and `DISCTOTAL` fields.

- **Fields**:
  - `DISCNUMBER` - Current disc number (simple numeric string, e.g., `"1"`, `"2"`, `"99"`)
  - `DISCTOTAL` - Total number of discs (optional, simple numeric string, e.g., `"2"`, `"3"`, `"99"`)
- **Range**: Unlimited (no hard limit, but practical limits apply)
- **Unified API Mapping**:
  - `DISCNUMBER="1"`, `DISCTOTAL="2"` → `DISC_NUMBER=1`, `DISC_TOTAL=2`
  - `DISCNUMBER="2"` → `DISC_NUMBER=2`, `DISC_TOTAL=None`
  - `DISCNUMBER="99"`, `DISCTOTAL="99"` → `DISC_NUMBER=99`, `DISC_TOTAL=99`
- **Examples**:
  - `DISCNUMBER="1"`, `DISCTOTAL="2"` → `DISC_NUMBER=1`, `DISC_TOTAL=2` (disc 1 of 2)
  - `DISCNUMBER="2"` → `DISC_NUMBER=2`, `DISC_TOTAL=None` (disc 2, total unknown)
  - `DISCNUMBER="99"`, `DISCTOTAL="99"` → `DISC_NUMBER=99`, `DISC_TOTAL=99` (disc 99 of 99)

**Advantages over ID3v2:**

- No 255 limit on disc numbers
- Separate fields allow for more flexible storage
- Can represent multi-disc sets with more than 255 discs (theoretical)
- Native support for separate fields matches the unified API design

## RIFF Disc Number Format

RIFF (WAV) format does not natively support disc numbers in its INFO chunk structure.

- **Support**: ✗ Not supported
- **Reason**: RIFF INFO chunk has no standard field for disc number
- **Workaround**: None available (format limitation)

## Unified Metadata API

The library provides two separate unified metadata fields for disc number handling:

- **`DISC_NUMBER`**: Integer representing the current disc number (required)
- **`DISC_TOTAL`**: Integer representing the total number of discs, or `None` if unknown (optional)

This two-field approach provides:

- **Type safety**: Both fields are integers, not strings requiring parsing
- **Flexibility**: Can set disc number without knowing total, or update total independently
- **Semantic clarity**: Disc number and total are conceptually separate pieces of information
- **Native Vorbis support**: Matches Vorbis' separate `DISCNUMBER` and `DISCTOTAL` fields

### Reading Disc Number

The library returns disc numbers as separate fields:

- `DISC_NUMBER`: Integer (e.g., `1`, `2`, `99`)
- `DISC_TOTAL`: Integer or `None` (e.g., `2`, `3`, `None`)

**Format Mapping:**

- **ID3v2**: Reads `TPOS` frame with `"disc/total"` format (e.g., `"1/2"`) → `DISC_NUMBER=1`, `DISC_TOTAL=2`
- **ID3v2**: Reads `TPOS` frame with `"disc"` format (e.g., `"1"`) → `DISC_NUMBER=1`, `DISC_TOTAL=None`
- **Vorbis**: Reads `DISCNUMBER` and `DISCTOTAL` fields directly → `DISC_NUMBER` and `DISC_TOTAL`
- **ID3v1**: Not supported
- **RIFF**: Not supported

### Writing Disc Number

The library writes disc numbers based on the unified metadata fields:

| Unified Metadata                | ID3v1 | ID3v2          | Vorbis                              | RIFF |
| ------------------------------- | ----- | -------------- | ----------------------------------- | ---- |
| `DISC_NUMBER=1`                 | ✗     | `TPOS="1"`     | `DISCNUMBER="1"`                    | ✗    |
| `DISC_NUMBER=1, DISC_TOTAL=2`   | ✗     | `TPOS="1/2"`   | `DISCNUMBER="1"`, `DISCTOTAL="2"`   | ✗    |
| `DISC_NUMBER=99, DISC_TOTAL=99` | ✗     | `TPOS="99/99"` | `DISCNUMBER="99"`, `DISCTOTAL="99"` | ✗    |
| `DISC_NUMBER=256`               | ✗     | `TPOS="255"`\* | `DISCNUMBER="256"`                  | ✗    |

\* ID3v2 truncates values exceeding 255 to 255

**Notes:**

- **ID3v1**: Disc number is not supported - no field available in the format
- **ID3v2**:
  - Combines `DISC_NUMBER` and `DISC_TOTAL` into `"disc/total"` format when writing (e.g., `"1/2"`)
  - If `DISC_TOTAL` is `None`, writes only disc number (e.g., `"1"`)
  - Values are limited to 0-255 range
  - Values exceeding 255 are typically truncated to 255
- **Vorbis**:
  - Writes `DISCNUMBER` and `DISCTOTAL` as separate fields (native format)
  - If `DISC_TOTAL` is `None`, only `DISCNUMBER` is written
  - No hard limit on disc numbers (unlimited in theory)
- **RIFF**: Disc number writing is not supported - no standard field in INFO chunk

## Format Comparison

| Format | Frame/Field           | Format Support | Range Limit | Unified API Mapping                           |
| ------ | --------------------- | -------------- | ----------- | --------------------------------------------- |
| ID3v1  | ✗                     | ✗              | N/A         | ✗                                             |
| ID3v2  | TPOS                  | ✓              | 0-255       | `"disc/total"` → `DISC_NUMBER`, `DISC_TOTAL`  |
| Vorbis | DISCNUMBER, DISCTOTAL | ✓              | Unlimited   | Separate fields → `DISC_NUMBER`, `DISC_TOTAL` |
| RIFF   | ✗                     | ✗              | N/A         | ✗                                             |

## Common Use Cases

1. **Single Disc Albums**: `DISC_NUMBER=1`, `DISC_TOTAL=1` or `DISC_NUMBER=1`, `DISC_TOTAL=None`
2. **Multi-Disc Albums**: `DISC_NUMBER=1`, `DISC_TOTAL=2` for disc 1 of 2-disc set
3. **Large Box Sets**: `DISC_NUMBER=1`, `DISC_TOTAL=10` for disc 1 of 10-disc set
4. **Unknown Total**: `DISC_NUMBER=1`, `DISC_TOTAL=None` when total number of discs is unknown

## API Usage Examples

```python
from audiometa import update_metadata, get_unified_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

# Set disc number with total
update_metadata("album.mp3", {
    UnifiedMetadataKey.DISC_NUMBER: 1,
    UnifiedMetadataKey.DISC_TOTAL: 2
})

# Set disc number without total
update_metadata("album.mp3", {
    UnifiedMetadataKey.DISC_NUMBER: 1
})

# Read disc number
metadata = get_unified_metadata("album.mp3")
disc_number = metadata.get(UnifiedMetadataKey.DISC_NUMBER)  # 1
disc_total = metadata.get(UnifiedMetadataKey.DISC_TOTAL)    # 2 or None
```

## Limitations Summary

- **ID3v1**: Cannot store disc numbers (format limitation)
- **ID3v2**: Limited to 255 discs maximum (both disc number and total)
- **Vorbis**: No hard limit, but practical limits apply based on implementation
- **RIFF**: Cannot store disc numbers (format limitation)
