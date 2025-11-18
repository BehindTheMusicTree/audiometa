# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Changelog Best Practices

- Changelogs are for humans, not machines.
- Include an entry for every version, with the latest first.
- Group similar changes under: Added, Changed, Improved, Deprecated, Removed, Fixed, Documentation, Performance, CI.
- **"Test" is NOT a valid changelog category** - tests should be mentioned within the related feature or fix entry, not as standalone entries.
- Use an "Unreleased" section for upcoming changes.
- Follow Semantic Versioning where possible.
- Use ISO 8601 date format: YYYY-MM-DD.
- Avoid dumping raw git logs; summarize notable changes clearly.
- **Tests should NOT be listed separately in "Added" section** - they should be mentioned with the related feature or fix entry.

**Note**: This changelog is maintained by project maintainers. Contributors should not update this file directly. See `.cursor/rules/changelog.mdc` for detailed changelog guidelines.

## [Unreleased]

## [0.2.6] - 2025-01-27

### Fixed

- **Mutagen Exception Handling (FLAC)**: Completed mutagen exception handling for FLAC operations that were missed in v0.2.5:
  - Added exception handling for FLAC duration reading using `handle_mutagen_exception()`
  - Added exception handling for FLAC MD5 checksum fixing operations
  - Ensures all mutagen exceptions in FLAC operations are properly converted to `FileCorruptedError`
  - Completes the comprehensive mutagen exception handling that was intended in v0.2.5
  - Includes unit tests covering FLAC duration and MD5 fixing exception scenarios
- **ConfigurationError Test Coverage**: Added comprehensive unit tests for `ConfigurationError` exception:
  - Tests `_convert_normalized_rating_to_file_rating()` raises `ConfigurationError` when `normalized_rating_max_value` is None (ID3v2, Riff, Vorbis managers)
  - Tests `_RiffManager._update_not_using_mutagen_metadata()` raises `ConfigurationError` when `metadata_keys_direct_map_write` is None
  - Completes test coverage for all documented exceptions in the Error Handling Guide

### Documentation

- **Error Handling Guide**: Created comprehensive error handling documentation:
  - Moved detailed exception documentation from README to dedicated `docs/ERROR_HANDLING_GUIDE.md`
  - Updated README with concise exception summary and link to detailed guide
  - Improves readability and maintains consistency with other detailed guides (Metadata Field Guide, Audio Technical Info Guide)

## [0.2.5] - 2025-11-18

### Fixed

- **Mutagen Exception Handling**: Added comprehensive exception handling for mutagen operations:
  - Created `_handle_mutagen_exception()` helper function to centralize exception handling
  - Wrapped `mutagen.save()` calls with proper exception handling in `_MetadataManager`
  - Added exception handling for `WAVE()` creation in `RiffManager`
  - Added exception handling for ID3v2 save operations in `_Id3v2Manager`
  - Standard I/O exceptions (`IOError`, `OSError`, `PermissionError`) are re-raised as-is
  - Mutagen-specific exceptions are converted to `FileCorruptedError` with descriptive messages
  - Prevents unhandled mutagen exceptions from propagating to users
  - Includes comprehensive unit tests (21 test cases) covering all exception handling scenarios, ID3-specific exceptions (ID3TagError, ID3BadCompressedData, ID3BadUnsynchData, ID3EncryptionUnsupportedError, ID3JunkFrameError, ID3UnsupportedVersionError), and WAVE-specific exceptions (IffError, InvalidChunk)

### Documentation

- **Exception Documentation**: Added comprehensive exception documentation:
  - Created dedicated "Error Handling (API Reference)" section
  - Added detailed explanations for all exception types with when they're raised and common causes
  - Documented exception handling for mutagen operations
  - Added examples showing how to handle all exception types
  - Updated table of contents with new exception documentation structure
- **PyPI Download Badges**: Fixed PyPI download badges showing "rate limited by upstream service":
  - Added cacheSeconds parameter to shields.io badges to reduce API calls and rate limiting
  - Maintains download statistics visibility with improved reliability

## [0.2.4] - 2025-11-17

### Fixed

- **Publish Workflow**: Fixed publish workflow to automatically wait for CI completion instead of failing immediately:
  - Added polling logic to wait for CI workflow to complete (checks every 30 seconds, max 30 minutes)
  - Prevents publish workflow from failing when CI is still running
  - Automatically proceeds with publishing once CI passes
  - Improves release process reliability and eliminates need for manual re-runs

## [0.2.3] - 2025-11-17

### Improved

- **Pre-commit Hooks**: Added shellcheck for shell script syntax checking:
  - Added shellcheck hook to catch syntax errors (missing `fi`, `done`, etc.) and common shell script issues
  - Prevents broken shell scripts from being committed
  - Only reports errors (not warnings) to keep checks focused on critical issues
- **Pre-commit Hooks**: Converted shell trailing blank lines check to auto-fix hook:
  - Changed `check-shell-trailing-blank-lines` to `fix-shell-trailing-blank-lines` hook
  - Automatically removes trailing blank lines instead of just checking
  - Ensures shell scripts end with exactly one newline (POSIX compliant)
  - Consistent with other formatting hooks (auto-fixes the issue)
- **CI Workflow**: Improved lint job to use shared installation script for consistency:
  - Lint job now uses `install-system-dependencies-ubuntu.sh lint` to install only lint dependencies (PowerShell)
  - Ensures consistency with local development and uses the same installation logic as test jobs
  - Pre-commit hooks skip system dependency verification in lint job (only lint dependencies are installed)
  - Renamed "Install dependencies" step to "Install Python dependencies" for clarity
  - Removed `fail-fast: false` to use default behavior (faster feedback, saves CI resources)
- **System Dependency Verification**: Clarified verification script documentation:
  - Updated documentation to specify that script verifies PROD and TEST-ONLY dependencies only
  - LINT dependencies (PowerShell) are not verified since they use "latest" version
  - Added clear error messages explaining what dependencies are verified

### Fixed

- **Ubuntu Installation Script**: Fixed syntax errors in `install-system-dependencies-ubuntu.sh`:
  - Added missing `fi` to close `if [ "$pinned_version" != "latest" ]` block
  - Added missing `fi` to close `if [[ "$CATEGORY" != "lint" ]]` block
  - Fixes "syntax error near unexpected token 'done'" and "unexpected end of file" errors
- **Windows Installation Script**: Improved error handling and made id3v2 optional:
  - Made `PINNED_ID3V2` optional in Windows installation script (requires WSL)
  - Added better error reporting to show Python script output on failures
  - Captures stderr (2>&1) to see Python errors when version loading fails
- **Pre-commit Hooks**: Fixed PowerShell ScriptAnalyzer hooks to fail with clear error messages instead of silently skipping:
  - Updated `psscriptanalyzer-wrapper.sh` and `psscriptanalyzer-format-wrapper.sh` to fail when PowerShell is not installed
  - Provides clear installation instructions for macOS (Homebrew) and other platforms
  - Ensures PowerShell script linting errors are caught locally, matching CI behavior
  - Previously, hooks silently skipped on macOS when PowerShell wasn't installed, allowing errors to only be caught in CI
- **Windows PowerShell Script**: Fixed version parsing logic in `install-system-dependencies-windows.ps1`:
  - Improved handling of Python script output (handles both string and array output)
  - Properly splits string output by newlines
  - Added better error messages for debugging version loading failures
  - Fixes CI failure where versions weren't being loaded correctly after replacing `Invoke-Expression`
- **System Dependencies**: Updated exiftool pinned version from 13.41 to 13.42:
  - Version 13.41 is no longer available on exiftool.org
  - Updated macOS and Windows pinned versions to 13.42 (latest available)
  - Fixes download failures when installing exiftool from exiftool.org

### Added

- **System Dependencies**: Added PowerShell Core installation to macOS and Ubuntu dependencies install scripts:
  - macOS: Automatically installs PowerShell Core via Homebrew cask when running `install-system-dependencies-macos.sh`
  - Ubuntu: Automatically installs PowerShell Core via Microsoft repository when running `install-system-dependencies-ubuntu.sh`
  - Required for PowerShell script linting in pre-commit hooks
  - Checks if PowerShell is already installed before attempting installation
  - Provides helpful warnings if PowerShell is installed but not in PATH

## [0.2.2] - 2025-11-17

### CI

- **PyPI Publishing Workflow**: Enhanced publishing workflow with TestPyPI testing and verification:
  - Added TestPyPI publishing step before real PyPI to catch issues early
  - Added TestPyPI installation verification to ensure package works correctly
  - Added post-publish verification check using PyPI API to confirm package availability
  - Includes retry logic to handle PyPI API propagation delays
  - Validates version and package name match expectations
  - Added verification that tag points to a commit on main branch (prevents publishing code not merged to main)
  - Added verification that CI has passed for the tagged commit (ensures code quality before publishing)
  - CI workflow now also runs on version tags to ensure code quality checks before publishing
  - Restricted publishing workflow to maintainer-only (prevents contributor modifications)
  - Publishing workflows handle sensitive secrets and can publish packages to PyPI
  - Documented maintainer-only policy in `CONTRIBUTING.md`
  - Aligns with security best practices for sensitive CI/CD workflows

### Fixed

- **Pre-commit Hooks**: Fixed trailing newline handling in pre-commit hooks:
  - Fixed `fix-long-comments.py` to prevent adding double trailing newlines when files have trailing blank lines
  - Strips trailing empty lines before writing to ensure files end with exactly one newline (PEP 8 compliant)

### Added

- **Pre-commit Hooks**: Added hook to fix trailing blank lines in shell scripts:
  - New `fix-trailing-blank-lines.sh` hook removes trailing blank lines from `.sh` and `.bash` files
  - Ensures shell scripts end with exactly one newline (POSIX compliant)
  - Automatically fixes trailing blank line issues during commits

### Documentation

- **Git Workflow**: Clarified branch naming conventions:
  - Added "When to Use Each Prefix" section to git workflow rules
  - Clarified when to use `feature/`, `chore/`, and `hotfix/` prefixes
  - Added examples for infrastructure/tooling fixes vs library code fixes
- **README**: Added PyPI-related badges:
  - Added PyPI version badge showing current package version
  - Added PyPI downloads badges (monthly and weekly) showing download statistics
  - Updated version badge to reflect current release version

## [0.2.1] - 2025-11-16

### Fixed

- **Pre-commit Hooks**: Fixed pre-commit hooks to require virtual environment for all Python tools:
  - Created generic `tool-wrapper.sh` that ensures venv tools are used (ruff, isort, mypy, docformatter)
  - Prevents using system tools with broken shebangs (e.g., mypy pointing to non-existent Python 3.12)
  - Provides clear error messages if virtual environment is missing
  - CI environments still work (falls back to system tools in CI)
- **System Dependency Verification**: Fixed verification script to avoid importing mutagen before Python dependencies are installed:
  - Uses `importlib.util` to load modules directly, bypassing `audiometa/__init__.py`
  - Creates namespace packages to prevent Python from executing package `__init__.py` files
  - Allows verification script to run during system dependency installation (before Python deps are installed)
- **macOS ExifTool Version Detection**: Fixed incorrect exiftool version detection on macOS:
  - Changed from `--version` flag to `-ver` flag (exiftool's correct flag)
  - Prevents false version detection (e.g., detecting 22.80 instead of 13.41) from copyright info
- **ExifTool Version Alignment**: Fixed exiftool version mismatch on macOS:
  - Updated macOS exiftool from 13.36 (Homebrew) to 13.41 (exiftool.org) to align with Windows
  - Modified macOS installation script to download exiftool directly from exiftool.org instead of Homebrew
  - Fixed lib directory installation to properly copy entire Perl module structure relative to script location
  - Ensures consistent exiftool version (13.41) across macOS and Windows platforms
- **Ubuntu Version Matching**: Improved Debian package version matching to handle partial versions and revision suffixes (e.g., "24.01" matches "24.01.1-1build2" or "24.01+dfsg-1build2")
- **Windows Version Matching**: Improved version matching to handle different precision levels ("7.1.0" matches "7.1" and vice versa)
- **Windows Version Detection**: Added fallback to detect versions from executables when Chocolatey detection fails

### Improved

- **Dependency Verification**: Created shared dependency verification infrastructure:
  - Created `scripts/verify-system-dependency-versions.py` as single source of truth for version verification
  - Used by pre-commit hooks, pytest config, and installation scripts for consistency
  - Moved OS-specific checkers from `audiometa/test/tests/` to `audiometa/utils/os_dependencies_checker/` (reusable utility)
  - Split into package structure with one class per file: `base.py`, `macos.py`, `ubuntu.py`, `windows.py`
  - Moved `load_dependencies_pinned_versions()` to `os_dependencies_checker/config.py` for better organization
  - Updated production code to use `get_tool_path()` to ensure pinned tool versions are used when calling external tools
  - Improved maintainability and organization
- **FLAC MD5 Validation**: Improved MD5 checksum validation reliability:
  - Unset MD5 checksums (all zeros) are now consistently treated as invalid
  - Improved detection logic to check `flac -t` return code first before parsing output
  - Combined stdout and stderr for more comprehensive output parsing
- **Dependencies**: Upgraded numpy from 1.26.4 to 2.3.4 for Python 3.13 compatibility

### Documentation

- **Technical Information Guide**: Created separate AUDIO_TECHNICAL_INFO_GUIDE.md to document technical information functions (duration, bitrate, MD5 validation) separately from metadata field handling
- **FLAC MD5 Validation**: Updated AUDIO_TECHNICAL_INFO_GUIDE.md to reflect consistent behavior for unset MD5 checksums

## [0.2.0] - 2025-11-15

### Added

- **Comprehensive Test Infrastructure**: Complete test suite reorganization with 500+ tests covering unit, integration, and end-to-end scenarios
- **Test Helper Framework**: `temp_file_with_metadata` context manager function for unified test file management with external tool operations
- **External Tool Integration**: Comprehensive external script suite for metadata manipulation and verification across all formats
- **Test Data Management**: 173 pre-created audio files covering edge cases, metadata combinations, and performance scenarios
- **Format-Specific Test Helpers**: Dedicated helper classes for ID3v1, ID3v2, Vorbis, and RIFF metadata operations
- **Command-Line Interface**: Full CLI implementation with read, write, delete, and unified metadata operations
- **CLI Testing Suite**: Complete command-line interface test coverage with error handling and edge case validation
- **New Metadata Fields**: Added support for BPM, UNSYNCHRONIZED_LYRICS, PUBLISHER, COPYRIGHT, COMPOSERS, REPLAYGAIN, ARCHIVAL_LOCATION
- **Enhanced Error Handling**: Comprehensive exception system with specific error types for different failure scenarios
- **Metadata Validation**: Input validation and type checking for all metadata operations
- **Enhanced `get_unified_metadata_field` API**: Added optional `metadata_format` parameter to query specific formats
- Format-specific metadata retrieval without extracting from dictionaries
- **ID3v1 writing support**: ID3v1 metadata can now be written and modified (previously read-only)
- Direct file manipulation for ID3v1 tags using 128-byte structure
- ID3v1 field truncation and validation (30-character limits for text fields, 4 characters for year)
- ID3v1 genre name to code conversion (automatic conversion to ID3v1 genre codes 0-255)
- ID3v1.1 track number support (1-255 range with null byte indicator)
- ID3v1 metadata deletion support
- ID3v1 encoding: Latin-1 encoding with error handling for non-ASCII characters
- ID3v1 compatibility: Works with MP3, FLAC, and WAV files containing ID3v1 tags
- ID3v2 version selection for MP3 files
- Support for choosing between ID3v2.3 (maximum compatibility) and ID3v2.4 (modern features)
- `id3v2_version` parameter in all metadata functions
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
- **Release Management**: Added bump2version tool for automated version management

### CI

- **CI/CD Pipeline**: Comprehensive GitHub Actions workflow for continuous integration:
  - Automated linting and code quality checks (ruff, isort, mypy, docformatter, assert statement validation)
  - Cross-platform testing on Ubuntu, macOS, and Windows
  - Multi-version Python support (3.12, 3.13)
  - Code coverage enforcement (85% threshold)
  - External tool verification (ffprobe, flac, metaflac, mid3v2)
  - Runs on push to main/feature/hotfix branches and all pull requests

### Changed

- **BREAKING: Python version requirement**: Minimum Python version increased from 3.10 to 3.12
  - Codebase uses `type` statements (PEP 695) which require Python 3.12+
  - CI now tests Python 3.12 and 3.13 only
  - Updated all documentation to reflect Python 3.12+ requirement
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

### Improved

- **Metadata Validation**: Enhanced input validation:
  - Type checking for all metadata fields
  - Range validation for rating values (0 to normalized max or non-negative)
  - Rating validation improvements: Non-negative integer requirement when normalized_rating_max_value is None
  - Format validation for track numbers (non-negative integers or string formats like "5/12")
  - Multi-value field handling with proper list validation
  - Empty value filtering for list-type metadata fields
  - Release date format validation with corresponding error handling
  - Year value validation with improved error handling for invalid values
- **External Tool Integration**: Optimized tool usage for maximum compatibility:
  - `metaflac` for Vorbis metadata writing to preserve proper key casing
  - `id3v2`/`mid3v2` for ID3v2 metadata writing in FLAC files to prevent corruption
  - `ffprobe` for RIFF metadata extraction with proper encoding handling

### Documentation

- **Contributing Guide**: Added comprehensive CONTRIBUTING.md with development workflow, code style guidelines, testing practices, and contribution process
- **Issue Templates**: Added bug report and feature request templates for better issue tracking and contributor experience
- **Pull Request Template**: Added comprehensive PR template aligned with contributing guidelines, including pre-PR checklist, breaking changes section, and testing instructions
- **Code of Conduct**: Added Contributor Covenant Code of Conduct to ensure a welcoming and inclusive community environment
- **Security Policy**: Added SECURITY.md with vulnerability reporting procedures, disclosure policy, and security best practices
- **Support Documentation**: Added SUPPORT.md with guidance on getting help, reporting issues, and asking questions
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
- **README Alignment**: Aligned mutagen version requirement documentation with pyproject.toml

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

- Python 3.12+
- mutagen >= 1.45.0
- ffprobe (for WAV file processing)
- flac (for FLAC MD5 validation)

### Migration Notes

- This is an unstable pre-release version
- API may change significantly in future releases
- Not recommended for production use until stable release
- Migrated from legacy audio metadata project with improved architecture
