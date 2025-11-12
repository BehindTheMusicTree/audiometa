# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Changelog Best Practices

- Changelogs are for humans, not machines.
- Include an entry for every version, with the latest first.
- Group similar changes under: Added, Changed, Improved, Deprecated, Removed, Fixed, Security, Documentation, Performance, CI.
- Use an "Unreleased" section for upcoming changes.
- Follow Semantic Versioning where possible.
- Use ISO 8601 date format: YYYY-MM-DD.
- Avoid dumping raw git logs; summarize notable changes clearly.

**Note**: This changelog is maintained by project maintainers. Contributors should not update this file directly.

## [Unreleased]

### Added

- **Comprehensive Test Infrastructure**: Complete test suite reorganization with 500+ tests covering unit, integration, and end-to-end scenarios
- **Test Helper Framework**: `TempFileWithMetadata` context manager for unified test file management with external tool operations
- **External Tool Integration**: Comprehensive external script suite for metadata manipulation and verification across all formats
- **Test Data Management**: 173 pre-created audio files covering edge cases, metadata combinations, and performance scenarios
- **Format-Specific Test Helpers**: Dedicated helper classes for ID3v1, ID3v2, Vorbis, and RIFF metadata operations
- **CLI Testing Suite**: Complete command-line interface test coverage with error handling and edge case validation
- **Command-Line Interface**: Full CLI implementation with read, write, delete, and unified metadata operations
- **New Metadata Fields**: Added support for BPM, UNSYNCHRONIZED_LYRICS, PUBLISHER, COPYRIGHT, COMPOSERS, REPLAYGAIN, ARCHIVAL_LOCATION
- **Enhanced Error Handling**: Comprehensive exception system with specific error types for different failure scenarios
- **Metadata Validation**: Input validation and type checking for all metadata operations
- **External Tool Integration**: Seamless integration with external tools (metaflac, id3v2, ffprobe) for optimal compatibility
- **Enhanced `get_unified_metadata_field` API**: Added optional `metadata_format` parameter to query specific formats
- Format-specific metadata retrieval without extracting from dictionaries
- **ID3v1 writing support**: ID3v1 metadata can now be written and modified (previously read-only)
- Direct file manipulation for ID3v1 tags using 128-byte structure
- ID3v1 field truncation and validation (30-character limits for text fields)
- ID3v1 genre name to code conversion
- ID3v1.1 track number support (1-255 range)
- ID3v1 metadata deletion support
- ID3v2 version selection for MP3 files
- Support for choosing between ID3v2.3 (maximum compatibility) and ID3v2.4 (modern features)
- `id3v2_version` parameter in all metadata functions
- Automatic version upgrade when reading existing files
- **Technical Information Functions**: Additional audio file analysis functions:
  - `get_file_size()`: Retrieve audio file size in bytes
  - `get_channels()`: Get number of audio channels (mono, stereo, etc.)
- **Comprehensive Metadata API**: `get_full_metadata()` function providing complete file analysis:
  - Unified metadata from all formats
  - Technical information (duration, bitrate, sample rate, channels, file size)
  - Format-specific headers and structure information
  - Raw metadata details from each format
  - Format priority information
- **GitHub Sponsors Support**: Added FUNDING.yml to enable GitHub Sponsors button on repository
- **Issue Templates**: Added bug report and feature request templates for better issue tracking and contributor experience
- **Pull Request Template**: Added comprehensive PR template aligned with contributing guidelines, including pre-PR checklist, breaking changes section, and testing instructions
- **CI/CD Pipeline**: Comprehensive GitHub Actions workflow for continuous integration:
  - Automated linting and code quality checks (ruff, isort, mypy, flake8, assert statement validation)
  - Cross-platform testing on Ubuntu, macOS, and Windows
  - Multi-version Python support (3.10, 3.11, 3.12, 3.13)
  - Code coverage enforcement (85% threshold)
  - External tool verification (ffprobe, flac, metaflac, mid3v2)
  - Runs on push to main/feature/hotfix branches and all pull requests

### Changed

- **Architecture simplification**: Removed MultiEntriesManager layer and integrated smart parsing into base MetadataManager
- Systematic smart parsing behavior for all semantically multi-value fields
- **ID3v1 is no longer read-only**: Full read/write support with direct file manipulation
- ID3v1 now supports all metadata writing strategies (SYNC, PRESERVE, CLEANUP)
- ID3v1 field mapping updated to use RELEASE_DATE instead of YEAR
- Default ID3v2 version changed from v2.4 to v2.3 for maximum compatibility
- ID3v2Manager now accepts `id3v2_version` parameter
- All public API functions now support `id3v2_version` parameter
- **Enhanced WAV file validation**: WAV files now properly validate and handle ID3v2 tags when present
- **RIFF metadata preservation**: RiffManager now merges existing metadata with new updates, ensuring preservation of existing data during metadata operations

### Implementation Improvements

- **New Metadata Fields**: Extended support for 8 additional metadata fields:
  - `BPM`: Beats per minute support across ID3v2, Vorbis, and RIFF formats
  - `UNSYNCHRONIZED_LYRICS`: Lyrics support with language code handling in ID3v2
  - `PUBLISHER`: Publisher information in ID3v2 and Vorbis formats
  - `COPYRIGHT`: Copyright information across ID3v2, Vorbis, and RIFF formats
  - `COMPOSERS`: Composer information with multi-value support
  - `REPLAYGAIN`: ReplayGain information in ID3v2 and Vorbis formats
  - `ARCHIVAL_LOCATION`: Archival location support in RIFF format
- **Command-Line Interface**: Complete CLI implementation with:
  - `audiometa read`: Full metadata reading with multiple output formats (JSON, YAML, table)
  - `audiometa unified`: Simplified unified metadata reading
  - `audiometa write`: Metadata writing with field-specific options
  - `audiometa delete`: Complete metadata removal
  - Recursive directory processing and batch operations
  - Error handling and continue-on-error options
- **Enhanced Error Handling**: Comprehensive exception system:
  - `InvalidRatingValueError`: Rating validation with proper range checking
  - `MetadataFieldNotSupportedByMetadataFormatError`: Format-specific field support validation
  - `MetadataFormatNotSupportedByAudioFormatError`: Audio format compatibility checking
  - `ConfigurationError`: External tool dependency validation
- **External Tool Integration**: Optimized tool usage for maximum compatibility:
  - `metaflac` for Vorbis metadata writing to preserve proper key casing
  - `id3v2`/`mid3v2` for ID3v2 metadata writing in FLAC files to prevent corruption
  - `ffprobe` for RIFF metadata extraction with proper encoding handling
- **Metadata Validation**: Enhanced input validation:
  - Type checking for all metadata fields
  - Range validation for numeric fields (ratings, BPM, track numbers)
  - Multi-value field handling with proper list validation
  - Empty value filtering for list-type metadata fields
  - Rating validation improvements: Non-negative integer requirement when normalized_rating_max_value is None
  - Release date format validation with corresponding error handling
  - Year value validation with improved error handling for invalid values
  - File content validation enhancements for supported audio formats
  - AudioFileMetadataParseError for improved metadata parsing error handling

### Documentation Enhancements

- **Comprehensive README**: Complete rewrite with detailed sections covering:
  - Installation instructions with system requirements and external tool setup
  - Quick start guide with practical examples
  - Complete API reference with all functions and parameters
  - Metadata field guide with format-specific support matrix
  - CLI documentation with examples and advanced options
  - Error handling guide with exception types and recovery strategies
  - External tools usage matrix and performance considerations
- **Test Documentation**: Comprehensive test organization guide:
  - Unit/integration/e2e test structure explanation
  - Test data strategy documentation
  - Helper class usage examples
  - External script documentation with detailed comments
- **Code Documentation**: Enhanced docstrings and inline documentation:
  - Detailed function and class documentation
  - Implementation details for complex algorithms
  - External tool integration explanations
  - Error handling and edge case documentation
- **Commit Message Conventions**: Standardized commit message format with test-specific prefixes
- **Cursor Rules**: Comprehensive development guidelines for code style, comments, and organization

### Test Infrastructure Details

- **Test Organization**: Complete reorganization following unit/integration/e2e testing patterns
- **Test Coverage**: 500+ tests covering all metadata formats, edge cases, and user scenarios
- **External Tool Scripts**: Comprehensive bash and Python scripts for metadata manipulation:
  - `set-id3v1-max-metadata.sh`: Maximum ID3v1 metadata for field limit testing
  - `set-id3v2-max-metadata.sh`: Comprehensive ID3v2 metadata with extended frames and ratings
  - `set-vorbis-max-metadata.sh`: Complete Vorbis comment metadata for FLAC files
  - `set-riff-max-metadata.sh`: Full RIFF INFO metadata for WAV files
- **Test Data Strategy**: Hybrid approach combining 173 pre-created files with on-the-fly generation
- **Helper Classes**: Format-specific metadata setters, getters, deleters, and verifiers
- **CLI Testing**: Complete command-line interface validation with error handling
- **Performance Testing**: Audio file readability verification after metadata updates
- **Cross-Platform Testing**: External tool dependency validation and error handling

### Technical Details

- **ID3v1 Implementation**: Uses direct file manipulation instead of mutagen for writing
- **Field Constraints**: Automatic truncation to 30 characters for text fields, 4 characters for year
- **Encoding**: Latin-1 encoding with error handling for non-ASCII characters
- **Genre Handling**: Automatic conversion from genre names to ID3v1 genre codes (0-255)
- **Track Numbers**: ID3v1.1 format with null byte indicator and 1-255 range validation
- **File Structure**: Maintains 128-byte fixed structure at end of file
- **Compatibility**: Works with MP3, FLAC, and WAV files containing ID3v1 tags

## [0.1.0] - 2024-10-03

### Added

- Initial migration release (UNSTABLE) by [Andreas Garcia](https://github.com/Andreas-Garcia)
- First step in migration from legacy audio metadata project
- Support for ID3v1, ID3v2, Vorbis, and RIFF formats
- Comprehensive metadata field support (50+ fields)
- Full read/write operations for most formats
- Rating support across different formats
- Type hints and comprehensive error handling
- Technical information access (bitrate, duration, sample rate, channels)
- FLAC MD5 validation support
- Support for cover art and lyrics
- MusicBrainz ID support
- ReplayGain information
- Multiple metadata field categories:
  - Basic information (title, artist, album, genre, rating)
  - Technical information (release date, track number, BPM, language)
  - Additional metadata (composer, publisher, copyright, lyrics, etc.)

### Supported Formats

- **ID3v1**: Read/Write with direct file manipulation (limited to 30 chars per field, Latin-1 encoding)
- **ID3v2**: Read/Write with full feature support including ratings (v2.2, v2.3, v2.4)
- **Vorbis**: Read/Write for FLAC files with rating support (OGG file support is planned but not yet implemented)
- **RIFF**: Read/Write for WAV files (no rating support)

### Requirements

- Python 3.10+
- mutagen >= 1.45.0
- ffprobe (for WAV file processing)
- flac (for FLAC MD5 validation)

### Migration Notes

- This is an unstable pre-release version
- API may change significantly in future releases
- Not recommended for production use until stable release
- Migrated from legacy audio metadata project with improved architecture
