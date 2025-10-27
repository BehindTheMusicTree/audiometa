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
    - [DO Test Errors When They Matter](#do-test-errors-when-they-matter)
    - [DON'T Test Redundant Errors](#dont-test-redundant-errors)
    - [The Rule of Thumb](#the-rule-of-thumb)
  - [Integration Test Logic](#integration-test-logic)
    - [When Integration Tests ARE Needed](#when-integration-tests-are-needed)
    - [When Integration Tests Are NOT Needed](#when-integration-tests-are-not-needed)
- [Test Data Strategy](#test-data-strategy)
  - [Pre-created Test Files](#pre-created-test-files)
  - [On-the-fly Generation (TempFileWithMetadata)](#on-the-fly-generation-tempfilewithmetadata)
  - [Examples for Each Scenario](#examples-for-each-scenario)
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

All test files are shared across test categories through fixtures defined in `conftest.py`.

## Fixtures

All test fixtures are defined in `conftest.py` and are available to all test files regardless of their location in the subfolder structure.
