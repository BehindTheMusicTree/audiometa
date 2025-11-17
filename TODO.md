# TODO

This file tracks future work, improvements, and testing tasks for AudioMeta Python.

**Note for Contributors**: This TODO list is maintained by project maintainers. If you'd like to suggest a new task or work on an existing one, please open a GitHub issue first for discussion. Maintainers will update this file based on project priorities and community feedback.

## Table of Contents

- [Features](#features)
  - [High Priority](#high-priority)
  - [Medium Priority](#medium-priority)
  - [Low Priority](#low-priority)
- [Testing & Quality](#testing--quality)
  - [High Priority](#high-priority-1)
  - [Medium Priority](#medium-priority-1)
  - [Low Priority](#low-priority-1)
- [Infrastructure](#infrastructure)
  - [High Priority](#high-priority-2)
  - [Medium Priority](#medium-priority-2)
  - [Low Priority](#low-priority-2)
- [Contributing](#contributing)

## Features

### High Priority

- [ ] **OGG file support**
  - Currently planned but not implemented
  - Vorbis comment support for OGG files
  - Integration with existing Vorbis manager

- [ ] **MP4 metadata format support**
  - Support for MP4/iTunes-style metadata tags
  - Integration with M4A/MP4 audio format support
  - Support for cover art, ratings, and extended metadata fields
  - Compatibility with iTunes and other Apple ecosystem tools

- [ ] **Support of non-supported fields**
  - Add support for metadata fields that are currently not handled by the library

### Medium Priority

- [ ] **M4A/MP4 audio format support**
  - Support for MPEG-4 audio files (M4A, MP4)
  - MP4 metadata format (iTunes-style tags)
  - Integration with existing metadata field system
  - Support for both audio-only and video files with audio tracks

- [ ] **AAC audio format support**
  - Support for Advanced Audio Coding files
  - MP4 container metadata handling
  - Integration with existing metadata managers

- [ ] **OGG Opus format support**
  - Support for Opus codec in OGG container
  - Vorbis comment metadata support
  - Integration with existing Vorbis manager

- [ ] **APE tag format support**
  - Support for APE (Monkey's Audio) tag format
  - Integration with APE audio format support
  - Support for APE-specific metadata fields

- [ ] **ASF (Advanced Systems Format) metadata support**
  - Support for ASF metadata format used in WMA files
  - Integration with WMA audio format support
  - Support for Windows Media-specific metadata fields

- [ ] **ID3v2.0 and ID3v2.2 support**
  - Full support for ID3v2.0 and ID3v2.2 frame handling
  - Version-specific features and limitations
  - Backward compatibility testing

- [ ] **Implement synchronized lyrics support in future versions**
  - Add support for SYLT (Synchronized Lyrics/Text) frames in ID3v2
  - Implement time-stamped lyrics for karaoke and synchronized text display
  - Support multiple synchronized lyrics entries with different languages

- [ ] **Implement full multi-language unsynchronized lyrics support in future versions**
  - Extend USLT (Unsynchronized Lyrics) frame support for multiple languages
  - Add language code handling (ISO 639-2) for lyrics and other text fields
  - Support multiple lyrics entries in different languages within the same file

- [ ] **Batch processing with parallelization**
  - Add Python API functions for processing multiple audio files (CLI already supports this)
  - Bridge the gap between CLI multi-file support and single-file Python API
  - Implement parallel metadata reading/writing operations for better performance
  - Add progress tracking and consolidated error handling for batch operations
  - Consider thread pool or multiprocessing for CPU-intensive tasks
  - Provide both sequential and parallel processing options

- [ ] **Broadcast Wave Format (BWF) support**
  - Implement reading and writing of BWF metadata for WAV files
  - Extend RIFF manager or create dedicated BWF manager
  - Add support for BWF-specific fields like time reference, originator, etc.

### Low Priority

- [ ] **APE (Monkey's Audio) format support**
  - Support for APE audio files
  - APE tag metadata format
  - Integration with existing metadata field system

- [ ] **WMA (Windows Media Audio) format support**
  - Support for WMA files
  - ASF metadata format
  - Integration with existing metadata managers

- [ ] **AIFF (Audio Interchange File Format) support**
  - Support for AIFF audio files
  - ID3v2 tag support in AIFF files
  - Integration with existing ID3v2 manager

- [ ] **Vorbis comment support for OGG Opus**
  - Extended Vorbis comment handling for Opus-specific fields
  - Integration with OGG Opus audio format support

- [ ] **AIFF metadata support**
  - Native AIFF metadata format support (if different from ID3v2)
  - Integration with AIFF audio format support

- [ ] **Provide a Docker image**
  - Create a Dockerfile for the project
  - Set up containerized environment for easy deployment and testing
  - Include necessary dependencies and entry points

- [ ] **Replace `--year` CLI argument with `--release-date`**
  - Replace `--year` argument with `--release-date` to accept both year-only (YYYY) and full date (YYYY-MM-DD) formats
  - Currently `--year` only accepts integer year values and converts to YYYY format
  - New `--release-date` should accept both "2024" and "2024-01-01" formats to match library's RELEASE_DATE support
  - Maintain backward compatibility or deprecate `--year` in favor of `--release-date`

## Testing & Quality

### High Priority

- [ ] **Test rating write profiles compatibility across different audio players**
  - Verify which rating values are actually readable and display correctly
  - Test BASE_255_NON_PROPORTIONAL (255 non-proportional) with Windows Media Player, MusicBee, Winamp, kid3
  - Test Profile B (100 proportional) with FLAC players and Vorbis-compatible software
  - Determine the best strategy regarding tools like Traktor with exotic rating handling like 255 proportional

### Medium Priority

- [ ] **Check multi-value separators compatibility with standard metadata readers**
  - Current implementation uses prioritized separators: "//", "\\\\", "\\", ";", "/", "," for joining multi-value fields
  - Smart parsing logic applies when null separators (\\x00) are present (always parse) or for single entries without nulls (legacy data detection)
  - Test compatibility with standard readers like iTunes, VLC, Windows Media Player to ensure correct parsing of multi-value metadata

- [ ] **Check compliance with each format's max length limitations with adapted exceptions and tests**
  - Verify ID3v1 (fixed sizes: e.g., title 30 bytes, artist 30 bytes), ID3v2 (variable but practical limits), RIFF, and Vorbis format constraints
  - Implement or adapt exceptions for length violations
  - Add unit and integration tests to validate length enforcement and error handling

- [ ] **Take a look at ID3v2.0 and ID3v2.2 and test it**
  - Review and test support for ID3v2.0 and ID3v2.2 frame handling and version-specific features

### Low Priority

_No low priority testing tasks at this time._

## Infrastructure

### High Priority

_No high priority infrastructure tasks at this time._

### Medium Priority

- [ ] **Check for Python 4.14 upgrade**
  - Review Python 4.14 release notes and breaking changes
  - Test library compatibility with Python 4.14
  - Update CI/CD workflows if needed
  - Update project dependencies and requirements

- [ ] **Review and update maintainer pre-merge checklist**
  - Ensure all maintainer checks are comprehensive and up-to-date
  - Align with current project practices and CI/CD setup
  - Document any additional checks needed before merging PRs

### Low Priority

_No low priority infrastructure tasks at this time._

## Contributing

If you'd like to work on any of these items:

1. Check if there's already an open issue for the task
2. Create a new issue if needed
3. Fork the repository and create a feature branch
4. Implement your changes with appropriate tests
5. Submit a pull request

For questions about specific tasks, please open an issue for discussion.
