# Audio Technical Info Guide: Support and Handling

This document provides comprehensive information about technical audio information support across all supported audio formats (MP3, FLAC, WAV). This includes duration, bitrate, sample rate, channels, file size, format information, and MD5 checksum validation and repair.

## Table of Contents

- [Technical Info Support by Audio Format](#technical-info-support-by-audio-format)
- [MD5 Checksum Validation and Repair](#md5-checksum-validation-and-repair)

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

### MD5 Checksum Repair

If a FLAC file has a corrupted or invalid MD5 checksum, you can repair it using the `fix_md5_checking()` function. This function recalculates and updates the MD5 checksum based on the current audio data.

```python
from audiometa import fix_md5_checking

# Repair MD5 checksum in FLAC file
fix_md5_checking("song.flac")
```

**Note**: The `fix_md5_checking()` function will also set an MD5 checksum for files that have an unset MD5 (all zeros), effectively enabling integrity checking for files that were encoded without MD5.

### MD5 Checksum States

FLAC files can have MD5 checksums in different states:

- **Valid MD5**: The checksum matches the audio data. The file integrity can be verified.
- **Invalid MD5**: The checksum exists but doesn't match the audio data (corrupted). The file may be corrupted or the checksum was incorrectly modified.
- **Unset MD5**: The checksum is all zeros (file was encoded without MD5 or MD5 was cleared). No integrity checking is available for these files.

The `is_flac_md5_valid()` function returns:

- `True` if the MD5 checksum is valid and matches the audio data
- `False` if the MD5 checksum is invalid (mismatch), unset (all zeros), or if the `flac` tool reports it as invalid
