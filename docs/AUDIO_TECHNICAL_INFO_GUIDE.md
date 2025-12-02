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

The library can validate MD5 checksums in FLAC files using the `is_flac_md5_valid()` function. This function checks whether the MD5 checksum stored in the FLAC file's STREAMINFO block matches the actual audio data.

```python
from audiometa import is_flac_md5_valid

# Check if FLAC file has valid MD5 checksum
is_valid = is_flac_md5_valid("song.flac")
if is_valid:
    print("MD5 checksum is valid")
else:
    print("MD5 checksum is invalid or unset")
```

**Note on Unset MD5**: When a FLAC file has an unset MD5 checksum (all zeros), the function returns `False` (invalid). An unset MD5 cannot verify file integrity, so it is considered invalid.

**Note on FLAC Files with ID3 Metadata**: FLAC files may contain ID3v1 or ID3v2 metadata tags, which are non-standard for the FLAC format. When ID3v2 tags are prepended to a FLAC file, the file no longer starts with the `fLaC` marker but with the `ID3` header instead.

This causes an issue because the `flac` tool (used internally via `flac -t`) may report errors such as "MD5 signature mismatch" or "FLAC\_\_STREAM_DECODER_ERROR_STATUS_LOST_SYNC" when processing FLAC files with ID3 tags.

The library handles this by searching for the `fLaC` marker in the file rather than assuming it's at position 0. This allows the library to correctly locate the STREAMINFO block and read the MD5 checksum even when ID3v2 tags are prepended to the file. Without this approach, the library would read bytes from inside the ID3 tag data instead of the actual MD5 checksum.

#### MD5 Checksum States

FLAC files can have MD5 checksums in different states:

- **Valid MD5**: The checksum matches the audio data. The file integrity can be verified.
- **Invalid MD5**: The checksum exists but doesn't match the audio data (corrupted). The file may be corrupted or the checksum was incorrectly modified.
- **Unset MD5**: The checksum is all zeros (file was encoded without MD5 or MD5 was cleared). No integrity checking is available for these files.

The `is_flac_md5_valid()` function returns:

- `True` if the MD5 checksum is valid and matches the audio data
- `False` if the MD5 checksum is invalid (mismatch), unset (all zeros), or if the `flac` tool reports it as invalid

### MD5 Checksum Repair

If a FLAC file has a corrupted, invalid, or missing (unset) MD5 checksum, you can repair it using the `fix_md5_checking()` function. This function recalculates and updates the MD5 checksum based on the current audio data.

```python
from audiometa import fix_md5_checking

# Repair MD5 checksum in FLAC file
fix_md5_checking("song.flac")
```

**Note**: The `fix_md5_checking()` function works for all invalid MD5 states:

- **Corrupted MD5**: Recalculates and sets the correct checksum
- **Invalid MD5**: Recalculates and sets the correct checksum
- **Missing/Unset MD5** (all zeros): Calculates and sets a new MD5 checksum, effectively enabling integrity checking for files that were encoded without MD5

**FLAC Files with ID3 Metadata**: When repairing MD5 checksums on FLAC files that contain ID3v1 or ID3v2 tags, the `flac` tool will decode and re-encode the audio stream. This process removes non-standard metadata formats like ID3 tags, keeping only the native Vorbis comments. If you need to preserve ID3 metadata after MD5 repair, you should back up the ID3 tags before repair and restore them afterward. However, note that adding ID3 tags back may cause MD5 validation to fail again, as ID3 tags are non-standard in FLAC and can interfere with the MD5 validation process.
