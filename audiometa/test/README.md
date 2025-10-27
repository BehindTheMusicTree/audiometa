# Test Organization

This directory contains the test suite for audiometa-python, organized using the standard unit/integration/e2e testing pattern.

## Table of Contents

- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
  - [Run all tests](#run-all-tests)
  - [Run tests by category](#run-tests-by-category)
  - [Run tests by folder](#run-tests-by-folder)
  - [Combine markers](#combine-markers)
- [Test Logic Principles](#test-logic-principles)
  - [When to Test Error Cases](#when-to-test-error-cases)
  - [Integration Test Logic](#integration-test-logic)
  - [Current Test Structure](#current-test-structure)
- [Test Data Strategy](#test-data-strategy)
  - [Pre-created Test Files](#pre-created-test-files)
  - [On-the-fly Generation (TempFileWithMetadata)](#on-the-fly-generation-tempfilewithmetadata)
  - [Temporary Files (Fixtures)](#temporary-files-fixtures)
  - [When to Use Each Approach](#when-to-use-each-approach)
  - [Testing API Patterns](#testing-api-patterns)
  - [Examples for Each Scenario](#examples-for-each-scenario)
  - [File Organization](#file-organization)
- [Fixtures](#fixtures)

## Test Structure

### Unit Tests (`unit/`)

Tests for individual components and classes in isolation. These are fast, focused tests that verify individual functions and methods work correctly.

- **Marker**: `@pytest.mark.unit`
- **Speed**: Very fast (milliseconds)

### Integration Tests (`integration/`)

Tests that verify how multiple components work together with real dependencies. These test component interactions and data flow.

- **Marker**: `@pytest.mark.integration`
- **Speed**: Medium (seconds)

### End-to-End Tests (`e2e/`)

Tests that verify complete user workflows from start to finish. These simulate real user scenarios and test the entire system.

- **Marker**: `@pytest.mark.e2e`
- **Speed**: Slow (minutes)

## Running Tests

### Run all tests

```bash
pytest
```

### Run tests by category

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only (medium speed)
pytest -m integration

# End-to-end tests only (slow)
pytest -m e2e
```

### Run tests by folder

```bash
# Unit tests
pytest audiometa/test/tests/unit/

# Integration tests
pytest audiometa/test/tests/integration/

# End-to-end tests
pytest audiometa/test/tests/e2e/
```

### Combine markers

```bash
# Run unit and integration tests (skip slow e2e)
pytest -m "unit or integration"

# Run everything except e2e tests
pytest -m "not e2e"

# Run only fast tests
pytest -m unit
```

## Test Logic Principles

### When to Test Error Cases

**Critical Principle**: Test behavior, not trivial pass-through paths.

#### ✅ DO Test Errors When They Matter

1. **Test unique error paths**: Each component should test errors that are specific to its logic

   ```python
   # ✅ Good - Tests AudioFile-specific file type validation
   def test_audio_file_unsupported_type(self, temp_audio_file: Path):
       with pytest.raises(FileTypeNotSupportedError):
           AudioFile(temp_audio_file)
   ```

2. **Test different error types**: FileNotFoundError is different from FileTypeNotSupportedError
   ```python
   # ✅ Good - Tests file existence, not type validation
   def test_get_duration_in_sec_nonexistent_file(self):
       with pytest.raises(FileNotFoundError):
           AudioFile("nonexistent.mp3").get_duration_in_sec()
   ```

#### ❌ DON'T Test Redundant Errors

1. **Don't test the same error in multiple places**: If error handling is centralized, test it once

   ```python
   # ❌ Bad - Redundant with AudioFile test
   def test_get_duration_in_sec_unsupported_file_type_raises_error(self):
       with pytest.raises(FileTypeNotSupportedError):
           get_duration_in_sec("file.txt")

   # The wrapper just calls AudioFile(file) which already tests this
   ```

2. **Don't test trivial pass-through**: If the wrapper just delegates to another component, don't re-test the delegate's behavior

   ```python
   # Wrapper implementation:
   def get_duration_in_sec(file: FILE_TYPE) -> float:
       if not isinstance(file, AudioFile):
           file = AudioFile(file)  # Error happens here
       return file.get_duration_in_sec()

   # ❌ Bad - Testing AudioFile behavior through wrapper
   # ✅ Good - Just test AudioFile directly, wrapper will propagate error
   ```

#### The Rule of Thumb

Ask yourself: **"Does this error path add unique value?"**

- **Unique value**: Component has specific error handling or transformation
- **No unique value**: Component just passes the error through unchanged

If it's just a pass-through, don't test it.

### Integration Test Logic

Integration tests should verify **integration** (component interactions), not duplicate unit tests.

#### When Integration Tests ARE Needed

```python
# ✅ Good - Tests that wrapper correctly handles different input types
def test_get_duration_in_sec_works_with_audio_file_object(self, sample_mp3_file: Path):
    audio_file = AudioFile(sample_mp3_file)
    duration = get_duration_in_sec(audio_file)  # Passing AudioFile directly
    assert duration > 0

# ✅ Good - Tests external tool verification
def test_get_duration_in_sec_matches_external_tool(self, sample_mp3_file: Path):
    external_duration = TechnicalInfoInspector.get_duration(sample_mp3_file)
    duration = get_duration_in_sec(sample_mp3_file)
    assert duration == pytest.approx(expected)
```

#### When Integration Tests Are NOT Needed

```python
# ❌ Bad - Just testing AudioFile again through wrapper
def test_get_duration_in_sec_unsupported_file_type_raises_error(self):
    with pytest.raises(FileTypeNotSupportedError):
        get_duration_in_sec("file.txt")
# This is already tested in unit tests for AudioFile
```

### Current Test Structure

**File Type Validation**:

- ✅ Unit test: `test_file_type_validation.py` - Tests AudioFile initialization
- ❌ Integration test: Not needed (wrappers just create AudioFile)

**Technical Info Functions**:

- ✅ Unit tests: Test AudioFile methods directly with edge cases
- ✅ Integration tests: Test wrapper with different input types (str, Path, AudioFile)
- ❌ Don't test: FileTypeNotSupportedError in integration (already covered)

## Test Data Strategy

The test suite uses a **hybrid approach** for test data management, combining pre-created files with on-the-fly generation to optimize for both performance and flexibility.

### Pre-created Test Files (`../data/audio_files/`)

**173 pre-created audio files** covering specific scenarios and edge cases:

- **Edge cases**: Corrupted files, bad extensions, unusual filenames
- **Metadata combinations**: Files with specific metadata formats and values
- **Performance scenarios**: Different bitrates, durations, and file sizes
- **Regression tests**: Known problematic files that previously caused issues
- **Format validation**: Files with multiple metadata formats in the same file

**Benefits:**

- ⚡ **Fast**: Instant access, no script execution overhead
- 🎯 **Reliable**: Pre-tested and known to work correctly
- 📊 **Comprehensive**: Covers complex scenarios that would be difficult to generate
- 🔄 **Stable**: Consistent across test runs

### On-the-fly Generation (TempFileWithMetadata)

**Dynamic test file creation** using the unified `TempFileWithMetadata` class:

- **Writing tests**: When testing the application's metadata writing functionality
- **Dynamic scenarios**: Specific metadata combinations not available in pre-created files
- **Clean state**: Fresh files for each test run
- **Isolation**: Prevents test setup from depending on the code being tested

**How TempFileWithMetadata Works:**

The `TempFileWithMetadata` class provides a unified interface for all test file operations:

1. **Unified API**: Single class that handles all metadata operations and file management
2. **External Tool Integration**: Uses external command-line tools internally for metadata setup
3. **Context Manager**: Automatic file cleanup and resource management
4. **Header Detection**: Built-in methods to verify metadata headers and formats

**Supported Format Types:**

- `'mp3'` → creates **ID3v2** metadata (uses `mid3v2`)
- `'id3v1'` → creates **ID3v1** metadata (uses `id3v2 --id3v1-only`)
- `'flac'` → creates **Vorbis** metadata (uses `metaflac`)
- `'wav'` → creates **RIFF** metadata (uses `bwfmetaedit`)

**Basic Usage:**

```python
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata

# Create test file with initial metadata
with TempFileWithMetadata({
    "title": "Test Title",
    "artist": "Test Artist",
    "album": "Test Album",
    "year": "2023",
    "genre": "Rock"
}, "mp3") as test_file:
    # Use test_file.path for testing
    metadata = get_unified_metadata(test_file.path)
    assert metadata.get(UnifiedMetadataKey.TITLE) == "Test Title"
```

**Advanced Operations:**

```python
with TempFileWithMetadata({}, "mp3") as test_file:
    # Set additional metadata using external tools
    test_file.set_id3v1_genre("17")  # Set ID3v1 genre by code
    test_file.set_id3v2_genre("Rock")  # Set ID3v2 genre by name
    test_file.set_id3v2_multiple_genres(["Rock", "Alternative", "Indie"])

    # Set maximum metadata using external scripts
    test_file.set_id3v1_max_metadata()
    test_file.set_id3v2_max_metadata()
    test_file.set_vorbis_max_metadata()
    test_file.set_riff_max_metadata()

    # Verify headers and metadata
    assert test_file.has_id3v2_header()
    assert test_file.has_id3v1_header()
    assert test_file.has_vorbis_comments()
    assert test_file.has_riff_info_chunk()

    # Get comprehensive header report
    headers = test_file.get_metadata_headers_present()
    # Returns: {'id3v2': True, 'id3v1': True, 'vorbis': False, 'riff': False}

    # Verify metadata removal
    test_file.remove_id3v2_metadata()
    removed = test_file.verify_headers_removed(['id3v2'])
    # Returns: {'id3v2': True} (successfully removed)

    # Check metadata with external tools
    tool_results = test_file.check_metadata_with_external_tools()
    # Returns comprehensive verification results
```

**Available Methods:**

**Metadata Setting:**

- `set_id3v1_genre(genre_code)` - Set ID3v1 genre by numeric code
- `set_id3v2_genre(genre)` - Set ID3v2 genre by name
- `set_id3v2_multiple_genres(genres)` - Set multiple ID3v2 genres
- `set_vorbis_artists_one_two_three()` - Set specific artist metadata
- `set_riff_genre_text(genre_text)` - Set RIFF genre text

**Maximum Metadata Setup:**

- `set_id3v1_max_metadata()` - Set comprehensive ID3v1 metadata
- `set_id3v2_max_metadata()` - Set comprehensive ID3v2 metadata
- `set_vorbis_max_metadata()` - Set comprehensive Vorbis metadata
- `set_riff_max_metadata()` - Set comprehensive RIFF metadata

**Metadata Removal:**

- `remove_id3v1_metadata()` - Remove ID3v1 metadata
- `remove_id3v2_metadata()` - Remove ID3v2 metadata
- `remove_riff_metadata()` - Remove RIFF metadata

**Header Detection:**

- `has_id3v2_header()` - Check for ID3v2 header
- `has_id3v1_header()` - Check for ID3v1 header
- `has_vorbis_comments()` - Check for Vorbis comments
- `has_riff_info_chunk()` - Check for RIFF INFO chunk

**Verification:**

- `get_metadata_headers_present()` - Get comprehensive header report
- `verify_headers_removed(expected_removed)` - Verify metadata removal
- `check_metadata_with_external_tools()` - External tool verification

**Benefits:**

- 🔧 **Unified Interface**: Single class for all test file operations
- 🧪 **Isolated**: Test setup doesn't depend on the code being tested
- 🆕 **Fresh**: Clean state for each test with automatic cleanup
- 🎛️ **Configurable**: Easy to modify test scenarios
- **Reliability**: Uses proven external tools for metadata setup
- **Maintainability**: Clear separation between test setup and test logic
- **Comprehensive**: Built-in verification and header detection methods

### TempFileWithMetadata Method Reference

The `TempFileWithMetadata` class provides comprehensive methods for all test file operations:

#### File Creation and Management

- `__init__(metadata, format_type)` - Initialize with metadata and format
- `path` - Property to access the test file path
- `__enter__()` / `__exit__()` - Context manager for automatic cleanup

#### Metadata Setting Methods

- `set_id3v1_genre(genre_code)` - Set ID3v1 genre by numeric code (0-147)
- `set_id3v2_genre(genre)` - Set ID3v2 genre by name
- `set_id3v2_multiple_genres(genres)` - Set multiple ID3v2 genres as list
- `set_vorbis_artists_one_two_three()` - Set specific artist metadata pattern
- `set_riff_genre_text(genre_text)` - Set RIFF genre as text

#### Maximum Metadata Setup

- `set_id3v1_max_metadata()` - Set comprehensive ID3v1 metadata using external script
- `set_id3v2_max_metadata()` - Set comprehensive ID3v2 metadata using external script
- `set_vorbis_max_metadata()` - Set comprehensive Vorbis metadata using external script
- `set_riff_max_metadata()` - Set comprehensive RIFF metadata using external script

#### Metadata Removal

- `remove_id3v1_metadata()` - Remove ID3v1 metadata using external script
- `remove_id3v2_metadata()` - Remove ID3v2 metadata using external script
- `remove_riff_metadata()` - Remove RIFF metadata using external script

#### Header Detection

- `has_id3v2_header()` - Check if file has ID3v2 header (returns bool)
- `has_id3v1_header()` - Check if file has ID3v1 header (returns bool)
- `has_vorbis_comments()` - Check if file has Vorbis comments (returns bool)
- `has_riff_info_chunk()` - Check if file has RIFF INFO chunk (returns bool)

#### Verification and Analysis

- `get_metadata_headers_present()` - Get comprehensive header report (returns dict)
- `verify_headers_removed(expected_removed)` - Verify metadata removal (returns dict)
- `check_metadata_with_external_tools()` - External tool verification (returns dict)

#### Usage Patterns

**Basic Test Setup:**

```python
with TempFileWithMetadata({"title": "Test"}, "mp3") as test_file:
    # test_file.path contains the file path
    # Automatic cleanup when exiting context
```

**Complex Metadata Testing:**

```python
with TempFileWithMetadata({}, "mp3") as test_file:
    # Set up complex metadata
    test_file.set_id3v2_max_metadata()
    test_file.set_id3v1_genre("17")  # Blues

    # Verify setup
    assert test_file.has_id3v2_header()
    assert test_file.has_id3v1_header()

    # Test your functionality
    result = your_function(test_file.path)
```

**Header Verification:**

```python
with TempFileWithMetadata({}, "mp3") as test_file:
    test_file.set_id3v2_max_metadata()

    # Check what headers are present
    headers = test_file.get_metadata_headers_present()
    # Returns: {'id3v2': True, 'id3v1': False, 'vorbis': False, 'riff': False}

    # Verify specific headers
    assert test_file.has_id3v2_header()
    assert not test_file.has_id3v1_header()
```

**Metadata Removal Testing:**

```python
with TempFileWithMetadata({}, "mp3") as test_file:
    test_file.set_id3v2_max_metadata()
    assert test_file.has_id3v2_header()

    # Remove metadata
    test_file.remove_id3v2_metadata()

    # Verify removal
    removed = test_file.verify_headers_removed(['id3v2'])
    # Returns: {'id3v2': True} (successfully removed)
    assert removed['id3v2']
```

### Temporary Files (Fixtures)

**Empty audio files** created during test execution:

- **Basic functionality**: Simple read/write operations
- **Error handling**: Testing with empty or invalid files
- **Clean slate**: Starting point for dynamic test scenarios

### When to Use Each Approach

| Scenario                      | Approach             | Reason                                                                        |
| ----------------------------- | -------------------- | ----------------------------------------------------------------------------- |
| Reading existing metadata     | Pre-created files    | Fast, reliable, comprehensive coverage                                        |
| Testing writing functionality | TempFileWithMetadata | Set up test data with external tools, then test app's writing by reading back |
| Edge case testing             | Pre-created files    | Complex scenarios already prepared                                            |
| Dynamic test scenarios        | TempFileWithMetadata | Flexible, on-demand creation                                                  |
| Basic functionality           | Temporary files      | Simple, clean, fast                                                           |
| Regression testing            | Pre-created files    | Known problematic files                                                       |

### Testing API Patterns

The codebase follows a **functional API approach** for all tests. Use these functions directly with file paths:

```python
# For reading metadata
metadata = get_unified_metadata(file_path)
title = get_unified_metadata_field(file_path, UnifiedMetadataKey.TITLE)

# For writing metadata
update_metadata(file_path, metadata_dict)

# For file operations
duration = get_duration_in_sec(file_path)
bitrate = get_bitrate(file_path)
```

**Note:** `AudioFile` objects are only used in unit tests for the `AudioFile` class itself. All other tests use the functional APIs above.

### Examples for Each Scenario

#### Reading existing metadata (Pre-created files)

```python
def test_read_metadata_from_pre_created_file(sample_mp3_file: Path):
    """Test reading metadata from a pre-created file with known metadata."""
    metadata = get_unified_metadata(sample_mp3_file)
    assert metadata.get(UnifiedMetadataKey.TITLE) == ["Sample Title"]
    assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["Sample Artist"]
```

#### Testing writing functionality (TempFileWithMetadata)

```python
def test_write_metadata_using_temp_file():
    """Test writing metadata by setting up with external tools, then testing our app."""
    # Use TempFileWithMetadata to set up test data
    with TempFileWithMetadata(
        {"title": "Original Title", "artist": "Original Artist"},
        "mp3"
    ) as test_file:
        # Now test our application's writing functionality
        new_metadata = {
            UnifiedMetadataKey.TITLE: "New Title"
        }
        update_metadata(test_file.path, new_metadata)

        # Verify by reading back
        metadata = get_unified_metadata(test_file.path)
        assert metadata.get(UnifiedMetadataKey.TITLE) == ["New Title"]
```

#### Edge case testing (Pre-created files)

```python
def test_corrupted_metadata_handling(corrupted_mp3_file: Path):
    """Test handling of corrupted metadata using pre-created problematic file."""
    # Test that our app gracefully handles corrupted metadata
    with pytest.raises(CorruptedMetadataError):
        get_unified_metadata(corrupted_mp3_file)
```

#### Dynamic test scenarios (TempFileWithMetadata)

```python
def test_specific_metadata_combination():
    """Test a specific metadata scenario not available in pre-created files."""
    # Create specific metadata combination on demand
    with TempFileWithMetadata(
        {
            "title": "Custom Title",
            "artist": "Custom Artist",
            "genre": "Custom Genre"
        },
        "mp3"
    ) as test_file:
        # Use additional methods to set more complex metadata
        test_file.set_id3v2_multiple_genres(["Rock", "Alternative", "Indie"])
        test_file.set_id3v1_genre("17")  # Blues genre code

        # Verify headers are present
        assert test_file.has_id3v2_header()
        assert test_file.has_id3v1_header()

        # Test our application
        metadata = get_unified_metadata(test_file.path)
        assert metadata.get(UnifiedMetadataKey.GENRES_NAMES) == ["Custom Genre"]
```

#### Basic functionality (Temporary files)

```python
def test_basic_read_write_operations(temp_audio_file: Path):
    """Test basic functionality with a simple temporary file."""
    # Test writing metadata
    test_metadata = {
        UnifiedMetadataKey.TITLE: "Test Title",
        UnifiedMetadataKey.ARTISTS: ["Test Artist"]
    }
    update_metadata(temp_audio_file, test_metadata)

    # Test reading metadata
    metadata = get_unified_metadata(temp_audio_file)
    assert metadata.get(UnifiedMetadataKey.TITLE) == ["Test Title"]
    assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["Test Artist"]
```

#### Regression testing (Pre-created files)

```python
def test_regression_issue_123(problematic_wav_file: Path):
    """Test a specific regression that was fixed in issue #123."""
    # This file previously caused a crash
    metadata = get_unified_metadata(problematic_wav_file)
    # Verify the fix works
    assert metadata is not None
```

### File Organization

```
../data/audio_files/           # Pre-created test files
├── sample.mp3                 # Basic sample files
├── metadata=*.mp3            # Metadata format scenarios
├── rating_*.wav              # Rating test cases
├── artists=*.mp3             # Artist metadata tests
└── duration=*.flac           # Duration test cases

../data/scripts/               # External scripts for generation
├── set-id3v2-max-metadata.sh
├── set-vorbis-max-metadata.sh
└── remove-*.py
```

All test files are shared across test categories through fixtures defined in `conftest.py`.

## Fixtures

All test fixtures are defined in `conftest.py` and are available to all test files regardless of their location in the subfolder structure.
