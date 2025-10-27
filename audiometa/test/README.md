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
  - [Unit Test Logic](#unit-test-logic)
    - [What Unit Tests Should Do](#what-unit-tests-should-do)
    - [What Unit Tests Should NOT Do](#what-unit-tests-should-not-do)
    - [Why Don't Unit Tests Verify Exact Values?](#why-dont-unit-tests-verify-exact-values)
  - [Integration Test Logic](#integration-test-logic)
    - [When Integration Tests ARE Needed](#when-integration-tests-are-needed)
    - [When Integration Tests Are NOT Needed](#when-integration-tests-are-not-needed)
  - [E2E Test Logic](#e2e-test-logic)
    - [What E2E Tests Should Do](#what-e2e-tests-should-do)
    - [What E2E Tests Should NOT Do](#what-e2e-tests-should-not-do)
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

### Unit Test Logic

Unit tests should test **individual components in isolation** with fast, focused tests that verify behavior without external dependencies.

#### What Unit Tests Should Do

```python
# ✅ Good - Test AudioFile class methods directly
def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
    audio_file = AudioFile(sample_mp3_file)
    duration = audio_file.get_duration_in_sec()
    assert isinstance(duration, float)
    assert duration > 0

# ✅ Good - Test error handling for this component
def test_get_duration_in_sec_nonexistent_file(self):
    with pytest.raises(FileNotFoundError):
        AudioFile("nonexistent.mp3").get_duration_in_sec()
```

#### What Unit Tests Should NOT Do

```python
# ❌ Bad - Don't use external tools in unit tests
def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
    external_duration = TechnicalInfoInspector.get_duration(sample_mp3_file)
    duration = AudioFile(sample_mp3_file).get_duration_in_sec()
    assert duration == external_duration
# Don't verify exact values - that's for integration tests

# ❌ Bad - Don't test through wrappers in unit tests
def test_get_duration_in_sec(self, sample_mp3_file: Path):
    duration = get_duration_in_sec(sample_mp3_file)  # Top-level function
    assert duration > 0
# Test AudioFile methods directly, not wrapper functions
```

**Unit Test Principles:**

- Test individual classes and their methods
- Fast execution (milliseconds)
- No external dependencies (dependencies should be mocked)
- Focus on behavior, not implementation
- Test error paths specific to the component

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

**Integration Test Principles:**

- Test component interactions
- Verify non trivial wrapper functions work correctly
- Use external tools for verification
- Test different input types (str, Path, AudioFile)
- Don't duplicate unit test coverage

### E2E Test Logic

End-to-end tests should verify **complete user workflows** from start to finish, simulating real-world usage scenarios.

#### What E2E Tests Should Do

```python
# ✅ Good - Test complete user workflow
def test_complete_metadata_editing_workflow(temp_audio_file: Path):
    # User reads metadata
    metadata = get_unified_metadata(temp_audio_file)
    assert metadata.get(UnifiedMetadataKey.TITLE) is None

    # User writes metadata
    update_metadata(temp_audio_file, {
        UnifiedMetadataKey.TITLE: "New Title",
        UnifiedMetadataKey.ARTISTS: ["New Artist"]
    })

    # User reads back to verify
    updated_metadata = get_unified_metadata(temp_audio_file)
    assert updated_metadata.get(UnifiedMetadataKey.TITLE) == ["New Title"]
    assert updated_metadata.get(UnifiedMetadataKey.ARTISTS) == ["New Artist"]

# ✅ Good - Test CLI workflows
def test_cli_read_and_write_workflow(temp_audio_file: Path):
    result = run_cli(["read", str(temp_audio_file)])
    assert result.exit_code == 0

    result = run_cli(["write", str(temp_audio_file), "--title", "New Title"])
    assert result.exit_code == 0

    result = run_cli(["read", str(temp_audio_file)])
    assert "New Title" in result.stdout
```

#### What E2E Tests Should NOT Do

```python
# ❌ Bad - Testing individual components
def test_audio_file_class_in_e2e(temp_audio_file: Path):
    audio_file = AudioFile(temp_audio_file)
    duration = audio_file.get_duration_in_sec()
    assert duration > 0
# This is a unit test concern

# ❌ Bad - Testing implementation details
def test_internal_manager_logic(temp_audio_file: Path):
    manager = MetadataManager(AudioFile(temp_audio_file))
    # Test internal behavior
# This should be in unit tests
```

**E2E Test Principles:**

- Test complete user scenarios
- Simulate real-world usage
- Test the full stack (CLI, API, file operations)
- Focus on workflows, not individual functions
- May be slower but provide confidence in system behavior
- Test happy paths and critical user journeys

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
