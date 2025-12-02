# Audio Technical Info Guide: Support and Handling

This document provides comprehensive information about technical audio information support across all supported audio formats (MP3, FLAC, WAV). This includes file validation, duration, bitrate, sample rate, channels, file size, format information, and MD5 checksum validation and repair.

## Table of Contents

- [File Validation](#file-validation)
- [Technical Info Support by Audio Format](#technical-info-support-by-audio-format)
- [MD5 Checksum Validation and Repair](#md5-checksum-validation-and-repair)
  - [MD5 Checksum Validation](#md5-checksum-validation)
    - [MD5 Checksum States](#md5-checksum-states)
  - [MD5 Checksum Repair](#md5-checksum-repair)

## File Validation

Before processing audio files, you can check if a file is a valid audio file supported by the library using the `is_audio_file()` function. This function validates that the file exists, has a supported extension (`.mp3`, `.flac`, `.wav`), and contains valid audio content for that format.

```python
from audiometa import is_audio_file

# Check if a file is a valid audio file
if is_audio_file("song.mp3"):
    print("Valid audio file")
    # Process the file
else:
    print("Not a valid audio file")
```

The function returns:

- `True` if the file is a valid audio file (exists, has supported extension, and contains valid audio content)
- `False` if the file doesn't exist, has an unsupported extension, or contains invalid/corrupted content

**Use cases:**

- Validate files before processing to avoid exceptions
- Filter file lists to only process valid audio files
- Check file integrity before metadata operations

## Technical Info Support by Audio Format

The library supports comprehensive technical audio information across different audio formats. The table below shows which technical information is supported by each audio format:

| Technical Info | MP3 | FLAC | WAV |
| -------------- | --- | ---- | --- |
| Duration       | ✓   | ✓    | ✓   |
| Bitrate        | ✓   | ✓    | ✓   |
| Sample Rate    | ✓   | ✓    | ✓   |
| Channels       | ✓   | ✓    | ✓   |
| File Size      | ✓   | ✓    | ✓   |
| Format Info    | ✓   | ✓    | ✓   |
| MD5 Checksum   |     | ✓    |     |
| MD5 Repair     |     | ✓    |     |

## MD5 Checksum Validation and Repair

For FLAC files, the library provides MD5 checksum validation and repair capabilities to ensure file integrity.

### MD5 Checksum Validation

The library can validate MD5 checksums in FLAC files using the `is_flac_md5_valid()` function. This function checks whether the MD5 checksum stored in the FLAC file's STREAMINFO block matches the actual audio data and returns a `FlacMd5State` enum value indicating the validation state.

```python
from audiometa import is_flac_md5_valid, FlacMd5State
from audiometa.exceptions import FileTypeNotSupportedError

# Check FLAC file MD5 validation state
try:
    state = is_flac_md5_valid("song.flac")

    if state == FlacMd5State.VALID:
        print("MD5 checksum is valid - file integrity verified")
    elif state == FlacMd5State.UNSET:
        print("MD5 checksum is not set (all zeros)")
    elif state == FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1:
        print("MD5 checksum cannot be validated due to ID3v1 tags")
    elif state == FlacMd5State.INVALID:
        print("MD5 checksum is invalid - file may be corrupted")
except FileTypeNotSupportedError:
    print("MD5 validation is only supported for FLAC files")
```

**Note on Non-FLAC Files**: MD5 checksum validation is only supported for FLAC files. If you attempt to validate a non-FLAC file (e.g., MP3 or WAV), the function will raise `FileTypeNotSupportedError`. The function checks the file extension before attempting validation, so the error is raised immediately without processing the file.

#### Validation Process Steps

The `is_flac_md5_valid()` function performs validation through the following detailed steps:

**Step 1: File Format Verification**

- Verifies that the file has a `.flac` extension
- Raises `FileTypeNotSupportedError` immediately if the file is not a FLAC file
- This check happens before any file processing, so non-FLAC files (MP3, WAV, etc.) fail fast with a clear error message

**Step 2: MD5 Unset Detection**

- Reads the FLAC file's binary data
- Searches for the `fLaC` marker in the file (starting from position 0, but may be offset if ID3v2 tags are prepended)
- Locates the STREAMINFO block by calculating the MD5 position: `fLaC_marker_position + 4 bytes (fLaC) + 1 byte (block header) + 18 bytes (STREAMINFO data before MD5)`
- Reads the 16-byte MD5 checksum from the STREAMINFO block
- If the MD5 checksum is all zeros (`\x00` \* 16), returns `FlacMd5State.UNSET` immediately (this state takes precedence over all others)

**Step 3: ID3v1 Tag Detection**

- Checks for ID3v1 tags at the end of the file by seeking to the last 128 bytes
  - If the last 128 bytes start with `b"TAG"`, ID3v1 tags are present
- Stores the ID3v1 tag presence status for later use in state determination

**Note**: Only ID3v1 tags are detected because only ID3v1 tags cause validation failures. ID3v2 tags do not interfere with `flac -t` validation and are not checked.

**Why detect ID3 tags here?**

ID3 tag detection is necessary to distinguish between actual file corruption and ID3 tag interference when `flac -t` validation fails:

- **ID3v1 tags**: Almost always cause `flac -t` to fail, even when the MD5 is valid. ID3v1 tags are appended at the end of the file and interfere with the FLAC stream structure, causing the `flac` tool to report errors. Detection ensures we return `UNCHECKABLE_DUE_TO_ID3V1` instead of incorrectly reporting `INVALID`.

- **ID3v2 tags**: Do NOT cause `flac -t` to fail. The `flac` tool can handle ID3v2 tags prepended at the start of the file, and validation succeeds (returns `VALID`). ID3v2 tags are not detected because they do not interfere with validation.

- **Without ID3v1 detection**: If `flac -t` fails and we don't know ID3v1 tags are present, we would incorrectly return `INVALID` for files that are actually valid but have ID3v1 tag interference.

**Step 4: MD5 Validation via flac Tool**

- Executes the `flac -t` command on the FLAC file to validate the MD5 checksum
- The `flac -t` command decodes the entire FLAC stream and verifies that the MD5 checksum in the STREAMINFO block matches the computed MD5 of the decoded audio data
- Captures both stdout and stderr output from the command
- Records the command's return code (0 = success, non-zero = failure)

**Step 5: State Determination Based on Validation Results**

The library determines the final state using the following decision tree:

1. **If MD5 is unset (from Step 2)** → Return `FlacMd5State.UNSET`

   - This check happens first and takes precedence over all other states

2. **If `flac -t` succeeds (return code 0) AND output contains "ok"** → Return `FlacMd5State.VALID`

   - The MD5 checksum matches the audio data
   - File integrity is verified

3. **If ID3v1 tags are present (from Step 3) AND `flac -t` fails with ID3-related errors** → Return `FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1`

   - Checks for the error message `"FLAC__STREAM_DECODER_ERROR_STATUS_LOST_SYNC"` in the output
   - OR if `flac -t` fails (non-zero return code) and ID3v1 tags are detected
   - The MD5 may actually be valid, but ID3v1 tag interference prevents verification
   - **Note**: Only ID3v1 tags cause this state. ID3v2 tags do not cause validation failures (they result in `VALID` state instead)

4. **If `flac -t` reports explicit MD5 mismatch** → Return `FlacMd5State.INVALID`

   - Checks for the error message `"MD5 signature mismatch"` in the output
   - The MD5 checksum does not match the audio data (file corruption)

5. **If `flac -t` fails with other errors (and no ID3 tags)** → Return `FlacMd5State.INVALID`

   - Any other validation failure without ID3 tags indicates corruption

6. **If `flac -t` succeeds (return code 0) but no "ok" message found** → Raise `FlacMd5CheckFailedError`
   - Unexpected state that should not occur in normal operation

**Note on FLAC Files with ID3 Metadata**: FLAC files may contain ID3v1 or ID3v2 metadata tags, which are non-standard for the FLAC format. When ID3v2 tags are prepended to a FLAC file, the file no longer starts with the `fLaC` marker but with the `ID3` header instead.

This causes an issue because the `flac` tool (used internally via `flac -t`) may report errors such as "MD5 signature mismatch" or "FLAC\_\_STREAM_DECODER_ERROR_STATUS_LOST_SYNC" when processing FLAC files with ID3 tags, even when the MD5 checksum is actually valid.

The library handles this by:

1. **Searching for the `fLaC` marker** in the file rather than assuming it's at position 0, allowing correct location of the STREAMINFO block and MD5 checksum even when ID3v2 tags are prepended
2. **Detecting ID3v1 tag presence** by checking the file end (last 128 bytes) before running validation
3. **Distinguishing between actual MD5 corruption and ID3v1-related validation failures** by checking for ID3v1 tags when `flac -t` fails
4. **Returning `FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1`** when the MD5 is set but cannot be validated due to ID3v1 tag interference, rather than incorrectly reporting it as invalid

#### MD5 Checksum States

The `is_flac_md5_valid()` function returns a `FlacMd5State` enum value indicating one of four possible states:

- **`FlacMd5State.VALID`**: The MD5 checksum is set and matches the audio data. The file integrity can be verified.

- **`FlacMd5State.UNSET`**: The MD5 checksum is all zeros (file was encoded without MD5 or MD5 was cleared). No integrity checking is available for these files.

- **`FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1`**: The MD5 checksum is set (not all zeros) but cannot be validated because the file contains ID3v1 tags that interfere with the `flac` tool's validation process. The MD5 may actually be valid, but the presence of ID3v1 tags (appended at the end of the file) interferes with the FLAC stream structure and prevents verification. **Note**: Only ID3v1 tags cause this state. ID3v2 tags (prepended at the start) do not interfere with validation and do not cause this state.

- **`FlacMd5State.INVALID`**: The MD5 checksum is set but doesn't match the audio data (corrupted). The file may be corrupted or the checksum was incorrectly modified.

**State Detection Logic Summary:**

The library determines the MD5 state using the following precedence order (checked in sequence):

1. **UNSET (highest precedence)**: If the MD5 checksum is all zeros → `FlacMd5State.UNSET`

   - Checked first, before any validation attempts
   - Takes precedence even if ID3 tags are present

2. **VALID**: If the `flac -t` tool reports success (return code 0 and "ok" in output) → `FlacMd5State.VALID`

   - MD5 checksum matches the audio data
   - File integrity is verified

3. **UNCHECKABLE_DUE_TO_ID3V1**: If the file has ID3v1 tags AND `flac -t` fails → `FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1`

   - ID3v1 tags (appended at file end) almost always interfere with validation
   - ID3v2 tags (prepended at file start) do not cause failures and are not checked
   - MD5 may actually be valid, but cannot be verified due to ID3v1 tag interference
   - Takes precedence over INVALID when ID3v1 tags are present

4. **INVALID (lowest precedence)**: If the `flac -t` tool reports MD5 mismatch or other errors (without ID3 tags) → `FlacMd5State.INVALID`
   - MD5 checksum does not match the audio data
   - Indicates file corruption or incorrect checksum

### MD5 Checksum Repair

If a FLAC file has a corrupted, invalid, or missing (unset) MD5 checksum, you can repair it using the `fix_md5_checking()` function. This function recalculates and updates the MD5 checksum based on the current audio data.

```python
from audiometa import fix_md5_checking

# Repair MD5 checksum in FLAC file
fix_md5_checking("song.flac")
```

**Note**: The `fix_md5_checking()` function works for all non-valid MD5 states:

- **`FlacMd5State.INVALID`**: Recalculates and sets the correct checksum
- **`FlacMd5State.UNSET`**: Calculates and sets a new MD5 checksum, effectively enabling integrity checking for files that were encoded without MD5
- **`FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1`**: Recalculates and sets the correct checksum (note: this will remove ID3v1 tags as part of the repair process)

**FLAC Files with ID3 Metadata**: When repairing MD5 checksums on FLAC files that contain ID3v1 or ID3v2 tags, the `flac` tool will decode and re-encode the audio stream. This process removes non-standard metadata formats like ID3 tags, keeping only the native Vorbis comments. If you need to preserve ID3 metadata after MD5 repair, you should back up the ID3 tags before repair and restore them afterward. However, note that adding ID3v1 tags back may cause MD5 validation to fail again, as ID3v1 tags are non-standard in FLAC and interfere with the MD5 validation process.

**Note on Non-FLAC Files**: The `fix_md5_checking()` function only works with FLAC files. Attempting to repair MD5 checksums on non-FLAC files (e.g., MP3 or WAV) will raise `FileTypeNotSupportedError`. MD5 checksums are a FLAC-specific feature and are not supported in other audio formats.
