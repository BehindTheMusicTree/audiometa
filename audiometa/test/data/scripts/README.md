# Test Scripts

This directory contains test scripts for the audiometa-python library. Each script includes comprehensive documentation as comments within the file itself.

## Scripts Overview

| Script                       | Purpose                 | Format         |
| ---------------------------- | ----------------------- | -------------- |
| `set-id3v1-max-metadata.sh`  | Set max ID3v1 metadata  | MP3            |
| `set-id3v2-max-metadata.sh`  | Set max ID3v2 metadata  | MP3, FLAC, WAV |
| `set-riff-max-metadata.sh`   | Set max RIFF metadata   | WAV            |
| `set-vorbis-max-metadata.sh` | Set max Vorbis metadata | FLAC           |

## Integration with Test Suite

These scripts are **standalone utilities** that complement the automated test suite:

- **Manual Testing**: Create test files with specific metadata configurations
- **Edge Case Testing**: Test field limits and unusual scenarios
- **Format Validation**: Verify metadata handling across different audio formats
- **Cleanup Operations**: Remove metadata for clean test environments

The automated test suite (`audiometa/test/tests/`) uses fixtures and temporary files, while these scripts provide additional manual testing capabilities.
