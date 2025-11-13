# Track Number Handling

The library handles different track number formats across audio metadata standards:

## ID3v1 Track Number Format

ID3v1 does not natively support track numbers. The library supports storing track numbers in the comment field since ID3v1.1 format.

- **Format**: Simple numeric string (e.g., `"5"`, `"12"`)
- **Parsing**: Returns as string
- **Examples**:
  - `"5"` → Track number: `"5"`
  - `"12"` → Track number: `"12"`

## ID3v2 Track Number Format

- **Format**: `"track/total"` (e.g., `"5/12"`, `"99/99"`) or simple `"track"` (e.g., `"5"`, `"1"`)
- **Parsing**: Returns the full track number string as stored
- **Examples**:
  - `"5/12"` → Track number: `"5/12"`
  - `"99/99"` → Track number: `"99/99"`
  - `"1"` → Track number: `"1"` (simple format also supported)

## Vorbis Track Number Format

- **Format**: Simple numeric string (e.g., `"5"`, `"12"`)
- **Parsing**: Returns as string
- **Examples**:
  - `"5"` → Track number: `"5"`
  - `"12"` → Track number: `"12"`

## RIFF Track Number Format

- **Format**: Simple numeric string (e.g., `"5"`, `"12"`)
- **Parsing**: Returns as string
- **Examples**:
  - `"5"` → Track number: `"5"`
  - `"12"` → Track number: `"12"`

## Reading and Writing Track Number

### Reading Track Number

The library returns track numbers as strings. The library handles common edge cases:

- `"5/"` → Track number: `"5/"` (trailing slash preserved)
- `"/12"` → Track number: `None` (no track number before slash)
- `"abc/def"` → Track number: `None` (non-numeric values)
- `""` → Track number: `None` (empty string)
- `"5/12/15"` → Track number: `None` (multiple slashes, invalid format)
- `"5-12"` → Track number: `"5-12"` (different separator preserved)
- `"01"` → Track number: `"01"` (leading zeros preserved)

### Writing Track Number

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
