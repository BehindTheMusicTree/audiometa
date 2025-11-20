# Testing Guide

This document provides comprehensive documentation for the test suite of audiometa-python, organized using the standard unit/integration/e2e testing pattern.

## Table of Contents

- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
  - [Run All Tests](#run-all-tests)
  - [Run Tests by Category](#run-tests-by-category)
  - [Run Tests by Folder](#run-tests-by-folder)
  - [Combine Markers](#combine-markers)
- [Code Coverage](#code-coverage)
  - [Running Tests with Coverage](#running-tests-with-coverage)
  - [Running Tests Without Coverage (Default)](#running-tests-without-coverage-default)
  - [Viewing Coverage Reports](#viewing-coverage-reports)
  - [Coverage in CI](#coverage-in-ci)
- [Test Logic Principles](#test-logic-principles)
  - [Unit Test Logic](#unit-test-logic)
    - [Unit Test Principles](#unit-test-principles)
    - [What Unit Tests Should Do](#what-unit-tests-should-do)
    - [What Unit Tests Should NOT Do](#what-unit-tests-should-not-do)
    - [Why Don't Unit Tests Verify Exact Values?](#why-dont-unit-tests-verify-exact-values)
  - [Integration Test Logic](#integration-test-logic)
    - [Integration Test Principles](#integration-test-principles)
    - [When Integration Tests ARE Needed](#when-integration-tests-are-needed)
    - [When Integration Tests Are NOT Needed](#when-integration-tests-are-not-needed)
  - [E2E Test Logic](#e2e-test-logic)
    - [E2E Test Principles](#e2e-test-principles)
    - [What E2E Tests Should Do](#what-e2e-tests-should-do)
    - [What E2E Tests Should NOT Do](#what-e2e-tests-should-not-do)
- [Test Data Strategy](#test-data-strategy)
  - [Pre-created Test Files](#pre-created-test-files)
  - [On-the-fly Generation (TempFileWithMetadata)](#on-the-fly-generation-tempfilewithmetadata)
  - [Examples for Each Scenario](#examples-for-each-scenario)
- [Windows Testing](#windows-testing)
  - [Windows WSL Requirement](#windows-wsl-requirement)
  - [Windows CI Differences](#windows-ci-differences)
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

Tests that verify complete user workflows from start to finish. These simulate real user scenarios and test the entire system. Speciffically they test the CLI operations.

- **Marker**: `@pytest.mark.e2e`
- **Speed**: Slow (minutes)

## Running Tests

**System dependency version verification:** Before running any tests, pytest automatically verifies that installed system dependency versions (ffmpeg, flac, mediainfo, id3v2, bwfmetaedit, exiftool) match the pinned versions defined in `system-dependencies-prod.toml` and `system-dependencies-test-only.toml`. This uses the shared `scripts/verify-system-dependency-versions.py` script (also used by pre-commit hooks and installation scripts). If versions don't match, pytest will exit with an error message before running tests. This ensures tests always run with the exact same tool versions as CI and local development environments.

**To fix version mismatches:** Update your system dependencies using the installation scripts:

- Ubuntu/Linux: `./scripts/install-system-dependencies-ubuntu.sh`
- macOS: `./scripts/install-system-dependencies-macos.sh`
- Windows: `.\scripts\install-system-dependencies-windows.ps1`

**Note:** On Windows, version verification skips optional tools (`id3v2`, `mediainfo`, `exiftool`) that are not needed for e2e tests. See the [Windows Testing](#windows-testing) section below for details.

### Run All Tests

```bash
pytest
```

### Run Tests by Category

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only (medium speed)
pytest -m integration

# End-to-end tests only (slow)
pytest -m e2e
```

### Run Tests by Folder

```bash
# Unit tests
pytest audiometa/test/tests/unit/

# Integration tests
pytest audiometa/test/tests/integration/

# End-to-end tests
pytest audiometa/test/tests/e2e/
```

### Combine Markers

```bash
# Run unit and integration tests (skip slow e2e)
pytest -m "unit or integration"

# Run everything except e2e tests
pytest -m "not e2e"

# Run only fast tests
pytest -m unit
```

## Code Coverage

Coverage is **not enabled by default** in pytest configuration to keep test runs fast and reduce noise during development. This is a best practice that allows:

- ⚡ **Faster development cycles**: Running individual tests without coverage overhead
- 🔇 **Less noise**: No coverage output when debugging a single test
- 📊 **Coverage on demand**: Run coverage when you need it, not every time

### Running Tests with Coverage

To run tests with coverage (recommended before committing or in CI):

```bash
pytest --cov=audiometa --cov-report=html --cov-report=term-missing --cov-fail-under=85
```

This will:

- Measure coverage for the `audiometa` package
- Display coverage summary in the terminal (including missing lines)
- Generate an HTML report in `htmlcov/` directory
- Fail if coverage is below 85%

### Running Tests Without Coverage (Default)

For faster development cycles, run tests without coverage:

```bash
pytest  # Fast, no coverage overhead
```

### Viewing Coverage Reports

After running with coverage, view the HTML report:

```bash
open htmlcov/index.html  # macOS
# or open htmlcov/index.html in your browser
```

### Coverage in CI

Coverage is automatically enforced in CI workflows, ensuring the 85% threshold is maintained across all pull requests and merges.

**CI test execution:** CI runs tests separately by marker (`unit`, `integration`, `e2e`) with coverage. The coverage threshold of 85% applies to the combined total.

**CI environment:** CI tests run on pinned OS versions (e.g., Ubuntu 22.04, macOS 14) for consistency. OS versions are pinned in `.github/workflows/ci.yml` to ensure system package version availability and consistency with pinned versions in `system-dependencies-prod.toml`, `system-dependencies-test-only.toml`, and `system-dependencies-lint.toml`. Python package versions are pinned in `pyproject.toml`. This prevents breakages when GitHub Actions updates `-latest` runners. See `.github/workflows/ci.yml` for the specific pinned OS versions.

## Test Logic Principles

### Unit Test Logic

Unit tests should test **individual components in isolation** with fast, focused tests that verify behavior without external dependencies.

#### Unit Test Principles

- Test individual classes and their methods
- Fast execution (milliseconds)
- No external tools or services (external tools should be mocked or avoided)
- Focus on behavior, not implementation
- Test error paths specific to the component
- When mocking, exact values from mocks are acceptable for testing controlled scenarios
- **File I/O operations are acceptable** when testing file operations directly (pragmatic approach)

#### Pragmatic Approach to File I/O in Unit Tests

For audio file libraries, file I/O operations are often **part of the functionality being tested**, not external dependencies. This codebase follows a pragmatic approach:

- ✅ **Use real small files** when testing file operations directly (e.g., `read()`, `write()`, `get_duration_in_sec()`)
- ✅ **Use real small files** when the operation inherently requires file access (e.g., metadata reading/writing)
- ❌ **Mock or avoid** external tools (e.g., `ffmpeg`, `mid3v2`, `vorbiscomment`)
- ❌ **Mock or avoid** network calls, databases, or other external services

#### What Unit Tests Should Do

```python
# ✅ Good - Test _AudioFile class methods directly with real files
def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
    audio_file = _AudioFile(sample_mp3_file)
    duration = audio_file.get_duration_in_sec()
    assert isinstance(duration, float)
    assert duration > 0

# ✅ Good - Test file I/O operations with real files (pragmatic approach)
def test_file_operations(self):
    with TempFileWithMetadata({}, "mp3") as test_file:
        audio_file = _AudioFile(test_file.path)
        test_data = b"test audio data"
        bytes_written = audio_file.write(test_data)
        assert bytes_written == len(test_data)
        read_data = audio_file.read()
        assert read_data == test_data

# ✅ Good - Test error handling for this component
def test_get_duration_in_sec_nonexistent_file(self):
    with pytest.raises(FileNotFoundError):
        _AudioFile("nonexistent.mp3").get_duration_in_sec()
```

#### What Unit Tests Should NOT Do

```python
# ❌ Bad - Don't use external tools in unit tests
def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
    external_duration = TechnicalInfoInspector.get_duration(sample_mp3_file)
    duration = _AudioFile(sample_mp3_file).get_duration_in_sec()
    assert duration == external_duration
# Don't verify exact values with external tools - that's for integration tests

# ❌ Bad - Don't test through wrappers in unit tests
def test_get_duration_in_sec(self, sample_mp3_file: Path):
    duration = get_duration_in_sec(sample_mp3_file)  # Top-level function
    assert duration > 0
# Test _AudioFile methods directly, not wrapper functions

# ❌ Bad - Don't use subprocess or external tools directly
def test_metadata_writing(self):
    with TempFileWithMetadata({}, "mp3") as test_file:
        import subprocess
        subprocess.run(["mid3v2", "--song=Test Title", str(test_file.path)], check=True)
        # Use TempFileWithMetadata methods instead
```

### Integration Test Logic

Integration tests should verify **integration** (component interactions), not duplicate unit tests.

#### Integration Test Principles

- Test component interactions
- Verify non trivial wrapper functions work correctly
- Use external tools for verification
- Test different input types (str, Path)
- Don't duplicate unit test coverage

#### When Integration Tests ARE Needed

```python
# ✅ Good - Tests that wrapper correctly handles different input types
def test_get_duration_in_sec_works_with_string_path(self, sample_mp3_file: Path):
    duration = get_duration_in_sec(str(sample_mp3_file))  # Passing string path
    assert duration > 0

def test_get_duration_in_sec_works_with_path_object(self, sample_mp3_file: Path):
    duration = get_duration_in_sec(sample_mp3_file)  # Passing Path object
    assert duration > 0

# ✅ Good - Tests external tool verification
def test_get_duration_in_sec_matches_external_tool(self, sample_mp3_file: Path):
    external_duration = TechnicalInfoInspector.get_duration(sample_mp3_file)
    duration = get_duration_in_sec(sample_mp3_file)
    assert duration == pytest.approx(expected)
```

#### When Integration Tests Are NOT Needed

```python
# ❌ Bad - Just testing _AudioFile again through wrapper
def test_get_duration_in_sec_unsupported_file_type_raises_error(self):
    with pytest.raises(FileTypeNotSupportedError):
        get_duration_in_sec("file.txt")
# This is already tested in unit tests for _AudioFile
```

### E2E Test Logic

End-to-end tests should verify **complete user workflows** from start to finish, simulating real-world usage scenarios.

#### E2E Test Principles

- Test complete user scenarios
- Simulate real-world usage
- Test the full stack (CLI, API, file operations)
- Focus on workflows, not individual functions
- May be slower but provide confidence in system behavior
- Test happy paths and critical user journeys

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
    audio_file = _AudioFile(temp_audio_file)
    duration = audio_file.get_duration_in_sec()
    assert duration > 0
# This is a unit test concern

# ❌ Bad - Testing implementation details
def test_internal_manager_logic(temp_audio_file: Path):
    manager = MetadataManager(_AudioFile(temp_audio_file))
    # Test internal behavior
# This should be in unit tests
```

## Test Data Strategy

The test suite uses a **hybrid approach** for test data management, combining pre-created files with on-the-fly generation to optimize for both performance and flexibility.

### Pre-created Test Files (`../assets/`)

**Various pre-created audio files** covering specific scenarios and edge cases:

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

### On-the-fly Generation (temp_file_with_metadata)

**Dynamic test file creation** using the `temp_file_with_metadata` context manager decorator:

- **Writing tests**: When testing the application's metadata writing functionality
- **Reading tests**: Needing specific metadata combinations not available in pre-created files
- **Clean state**: Fresh files for each test run
- **Isolation**: Prevents test setup from depending on the code being tested
- **Automatic cleanup**: Uses `@contextmanager` decorator for simple, reliable resource management

**Basic Usage:**

```python
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata

# Create test file with initial metadata
with temp_file_with_metadata({
    "title": "Test Title",
    "artist": "Test Artist",
    "album": "Test Album",
    "year": "2023",
    "genre": "Rock"
}, "mp3") as test_file:
    # Use test_file directly for testing
    metadata = get_unified_metadata(test_file)
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

#### Testing writing functionality (temp_file_with_metadata)

```python
def test_write_metadata_using_temp_file():
    """Test writing metadata by setting up with external tools, then testing our app."""
    # Use temp_file_with_metadata to set up test data
    with temp_file_with_metadata(
        {"title": "Original Title", "artist": "Original Artist"},
        "mp3"
    ) as test_file:
        # Now test our application's writing functionality
        new_metadata = {
            UnifiedMetadataKey.TITLE: "New Title"
        }
        update_metadata(test_file, new_metadata)

        # Verify by reading back
        metadata = get_unified_metadata(test_file)
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

#### Dynamic test scenarios (temp_file_with_metadata)

```python
def test_specific_metadata_combination():
    """Test a specific metadata scenario not available in pre-created files."""
    # Create specific metadata combination on demand
    with temp_file_with_metadata(
        {
            "title": "Custom Title",
            "artist": "Custom Artist",
            "genre": "Custom Genre"
        },
        "mp3"
    ) as test_file:
        # Use test_file for testing
        metadata = get_unified_metadata(test_file)
        assert metadata.get(UnifiedMetadataKey.GENRES_NAMES) == ["Custom Genre"]
```

All test files are shared across test categories through fixtures defined in `conftest.py`.

## Windows Testing

### Windows WSL Requirement

On Windows, the `id3v2` tool is not available as a native Windows binary. The installation script attempts to use **WSL (Windows Subsystem for Linux)** to install `id3v2` via Ubuntu's package manager, but WSL installation complexity (requiring system restarts, DISM configuration, and Ubuntu distribution setup) has prevented successful full installation in practice. This is why Windows CI only runs e2e tests (which don't require `id3v2`). For local development, the script will attempt WSL installation, but manual WSL setup may be required. A wrapper script (`id3v2.bat`) is created if WSL installation succeeds to make `id3v2` accessible from Windows command line.

### Windows CI Differences

Windows CI only runs e2e tests (unit and integration tests run on Ubuntu and macOS). This is due to WSL installation complexity preventing full dependency installation. As a result, some dependencies are skipped in Windows CI:

- **Skipped in Windows CI:**
  - `mediainfo` - Only used in integration tests for verification, not needed for e2e tests
  - `exiftool` - Not used in e2e tests
  - `id3v2` - Optional (only needed for FLAC files with ID3v2 tags, which e2e tests don't use)

- **Required in Windows CI:**
  - `ffmpeg` / `ffprobe` - Needed for `get_bitrate()` and `get_duration_in_sec()` on WAV files
  - `flac` / `metaflac` - Needed for FLAC metadata writing via Vorbis
  - `bwfmetaedit` - Needed for WAV metadata writing via RIFF

The installation script automatically detects CI environment and skips unnecessary dependencies. Version verification in pytest also skips these optional tools on Windows.

## Fixtures

All test fixtures are defined in `conftest.py` and are available to all test files regardless of their location in the subfolder structure.
