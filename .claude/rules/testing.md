# Test Organization

## Test File Structure

**One test class per test file.**

Each test file should contain exactly one test class. This improves:

- File organization and discoverability
- Easier navigation when looking for specific tests
- Clearer separation of concerns
- Better alignment with test class names and file names

### ✅ CORRECT - One class per file:

```python
# test_is_audio_file.py
@pytest.mark.unit
class TestIsAudioFile:
    def test_valid_mp3_file_returns_true(self, sample_mp3_file: Path):
        # ...

# test_file_validation.py
@pytest.mark.unit
class TestAudioFileFileTypeValidation:
    def test_extension_mp3_then_ok(self, sample_mp3_file: Path):
        # ...
```

### ❌ WRONG - Multiple classes per file:

```python
# test_file_validation.py
@pytest.mark.unit
class TestAudioFileFileTypeValidation:
    # ...

@pytest.mark.unit
class TestIsAudioFile:
    # ...
```

## Test Types and Markers

Tests are organized into three categories with clear markers:

- **Unit Tests** (`@pytest.mark.unit`): Fast (milliseconds), test individual components in isolation
- **Integration Tests** (`@pytest.mark.integration`): Medium speed (seconds), test component interactions
- **E2E Tests** (`@pytest.mark.e2e`): Slow (minutes), test complete user workflows

## Unit Test Principles

Unit tests should test **individual components in isolation** with fast, focused tests that verify behavior without external dependencies.

### Unit Test Principles

- Test individual classes and their methods
- Fast execution (milliseconds)
- No external tools or services (external tools should be mocked or avoided)
- Focus on behavior, not implementation
- Test error paths specific to the component
- When mocking, exact values from mocks are acceptable for testing controlled scenarios
- **File I/O operations are acceptable** when testing file operations directly (pragmatic approach)

### Pragmatic Approach to File I/O in Unit Tests

For audio file libraries, file I/O operations are often **part of the functionality being tested**, not external dependencies. This codebase follows a pragmatic approach:

- ✅ **Use real small files** when testing file operations directly (e.g., `read()`, `write()`, `get_duration_in_sec()`)
- ✅ **Use real small files** when the operation inherently requires file access (e.g., metadata reading/writing)
- ❌ **Mock or avoid** external tools (e.g., `ffmpeg`, `mid3v2`, `vorbiscomment`)
- ❌ **Mock or avoid** network calls, databases, or other external services

### What Unit Tests Should Do

```python
# ✅ Test _AudioFile class methods directly with real files
def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
    audio_file = _AudioFile(sample_mp3_file)
    duration = audio_file.get_duration_in_sec()
    assert isinstance(duration, float)
    assert duration > 0

# ✅ Test file I/O operations with real files (pragmatic approach)
def test_file_operations(self):
    with TempFileWithMetadata({}, "mp3") as test_file:
        audio_file = _AudioFile(test_file.path)
        test_data = b"test audio data"
        bytes_written = audio_file.write(test_data)
        assert bytes_written == len(test_data)
        read_data = audio_file.read()
        assert read_data == test_data

# ✅ Test error handling for this component
def test_get_duration_in_sec_nonexistent_file(self):
    with pytest.raises(FileNotFoundError):
        _AudioFile("nonexistent.mp3").get_duration_in_sec()
```

### What Unit Tests Should NOT Do

```python
# ❌ Don't use external tools in unit tests
def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
    external_duration = TechnicalInfoInspector.get_duration(sample_mp3_file)
    duration = _AudioFile(sample_mp3_file).get_duration_in_sec()
    assert duration == external_duration
# Don't verify exact values with external tools - that's for integration tests

# ❌ Don't test through wrappers in unit tests
def test_get_duration_in_sec(self, sample_mp3_file: Path):
    duration = get_duration_in_sec(sample_mp3_file)  # Top-level function
    assert duration > 0
# Test _AudioFile methods directly, not wrapper functions
```

## Integration Test Principles

Integration tests should verify **component interactions**, not duplicate unit tests.

### Integration Test Principles

- Test component interactions
- Verify non-trivial wrapper functions work correctly
- Use external tools for verification
- Test different input types (str, Path, \_AudioFile)
- Don't duplicate unit test coverage

### When Integration Tests ARE Needed

```python
# ✅ Tests that wrapper correctly handles different input types
def test_get_duration_in_sec_works_with_audio_file_object(self, sample_mp3_file: Path):
    audio_file = _AudioFile(sample_mp3_file)
    duration = get_duration_in_sec(audio_file)  # Passing _AudioFile directly
    assert duration > 0

# ✅ Tests external tool verification
def test_get_duration_in_sec_matches_external_tool(self, sample_mp3_file: Path):
    external_duration = TechnicalInfoInspector.get_duration(sample_mp3_file)
    duration = get_duration_in_sec(sample_mp3_file)
    assert duration == pytest.approx(external_duration)
```

### When Integration Tests Are NOT Needed

```python
# ❌ Just testing _AudioFile again through wrapper
def test_get_duration_in_sec_unsupported_file_type_raises_error(self):
    with pytest.raises(FileTypeNotSupportedError):
        get_duration_in_sec("file.txt")
# This is already tested in unit tests for _AudioFile
```

## E2E Test Principles

End-to-end tests should verify **complete user workflows** from start to finish, simulating real-world usage scenarios.

### E2E Test Principles

- Test complete user scenarios
- Simulate real-world usage
- Test the full stack (CLI, API, file operations)
- Focus on workflows, not individual functions
- May be slower but provide confidence in system behavior
- Test happy paths and critical user journeys

### What E2E Tests Should Do

```python
# ✅ Test complete user workflow
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
```

### What E2E Tests Should NOT Do

```python
# ❌ Testing individual components
def test_audio_file_class_in_e2e(temp_audio_file: Path):
    audio_file = _AudioFile(temp_audio_file)
    duration = audio_file.get_duration_in_sec()
    assert duration > 0
# This is a unit test concern
```

## Test Data Strategy

The test suite uses a **hybrid approach** for test data management, combining pre-created files with on-the-fly generation.

### Pre-created Test Files (`../assets/`)

**Use pre-created files for:**

- Reading existing metadata from files with known metadata
- Edge cases: Corrupted files, bad extensions, unusual filenames
- Metadata combinations: Files with specific metadata formats and values
- Performance scenarios: Different bitrates, durations, and file sizes
- Regression tests: Known problematic files that previously caused issues
- Format validation: Files with multiple metadata formats in the same file

**Benefits:**

- ⚡ Fast: Instant access, no script execution overhead
- 🎯 Reliable: Pre-tested and known to work correctly
- 📊 Comprehensive: Covers complex scenarios that would be difficult to generate
- 🔄 Stable: Consistent across test runs

**Example:**

```python
def test_read_metadata_from_pre_created_file(sample_mp3_file: Path):
    metadata = get_unified_metadata(sample_mp3_file)
    assert metadata.get(UnifiedMetadataKey.TITLE) == ["Sample Title"]
```

### On-the-fly Generation (TempFileWithMetadata)

**Use TempFileWithMetadata for:**

- **Writing tests**: When testing the application's metadata writing functionality
- **Setup for reading/deleting tests**: When you need initial metadata setup before testing reading or deletion
- Dynamic scenarios: Specific metadata combinations not available in pre-created files
- Clean state: Fresh files for each test run
- Isolation: Prevents test setup from depending on the code being tested

**When setting up metadata in tests, use helper classes:**

- All metadata setup operations in tests must use helper classes from `audiometa.test.helpers` (e.g., `ID3v2MetadataSetter`, `RIFFMetadataSetter`) - not subprocess or external tools directly
- Always use context managers (`TempFileWithMetadata`) for temporary files
- Access file path via `test_file.path` property

**Example:**

```python
def test_write_metadata_using_temp_file():
    with TempFileWithMetadata(
        {"title": "Original Title", "artist": "Original Artist"},
        "mp3"
    ) as test_file:
        update_metadata(test_file.path, {
            UnifiedMetadataKey.TITLE: "New Title"
        })
        metadata = get_unified_metadata(test_file.path)
        assert metadata.get(UnifiedMetadataKey.TITLE) == ["New Title"]
```

### Examples for Each Scenario

**Reading existing metadata (Pre-created files):**

```python
def test_read_metadata_from_pre_created_file(sample_mp3_file: Path):
    metadata = get_unified_metadata(sample_mp3_file)
    assert metadata.get(UnifiedMetadataKey.TITLE) == ["Sample Title"]
```

**Testing writing functionality (TempFileWithMetadata):**

```python
def test_write_metadata_using_temp_file():
    with TempFileWithMetadata(
        {"title": "Original Title", "artist": "Original Artist"},
        "mp3"
    ) as test_file:
        update_metadata(test_file.path, {
            UnifiedMetadataKey.TITLE: "New Title"
        })
        metadata = get_unified_metadata(test_file.path)
        assert metadata.get(UnifiedMetadataKey.TITLE) == ["New Title"]
```

## Test Isolation and Avoiding Circular Dependencies

### Use Helper Classes for Initial Data Setup (When Needed)

For tests that verify **reading, writing, or deleting functionality** using temporary files (not pre-created assets or mocks), NEVER use the library's own `update_metadata()` function to set up initial test data. This ensures proper test isolation and prevents testing the library's own writing logic when testing other functionality.

**When to use helper classes:**

- ✅ **Integration/E2E tests** that need to set up metadata on temporary files for reading/deleting tests
- ❌ **Unit tests with mocks** - use mocks directly
- ❌ **Tests using pre-created assets** (fixtures like `sample_mp3_file`) - use the assets directly
- ❌ **Writing tests** - test the `update_metadata()` function itself (that's what you're testing)

**Use helper classes from `audiometa.test.helpers`:**

- `ID3v2MetadataSetter` for ID3v2 metadata
- `ID3v1MetadataSetter` for ID3v1 metadata
- `VorbisMetadataSetter` for Vorbis/FLAC metadata
- `RIFFMetadataSetter` for RIFF/WAV metadata

**Note**: Helper classes use external tools internally for proper test isolation.

### ❌ Avoid using shutil for test files:

```python
def test_wav_sync_multiple_values(self, sample_wav_file: Path, temp_audio_file: Path):
    test_file = temp_audio_file.with_suffix('.wav')
    shutil.copy2(sample_wav_file, test_file)  # Don't do this
```

### ❌ WRONG - Don't use subprocess or external tools directly for metadata setup:

```python
def test_metadata_writing(self):
    with TempFileWithMetadata({}, "mp3") as test_file:
        # ❌ NEVER use subprocess or external tools directly for metadata setup
        import subprocess
        subprocess.run([
            "mid3v2",
            "--song=Test Title",
            "--artist=Test Artist",
            str(test_file.path)
        ], check=True)
```

### ❌ WRONG - Don't use external tool commands directly in tests:

```python
def test_id3v2_txxx_reading(self):
    with temp_file_with_metadata({}, "mp3") as test_file:
        # ❌ NEVER use external tool commands directly in tests
        from audiometa.utils.tool_path_resolver import get_tool_path
        from audiometa.test.helpers.common.external_tool_runner import run_external_tool

        command = [
            get_tool_path("mid3v2"),
            "--TXXX",
            f"MusicBrainz Track Id:{track_id}",
            str(test_file),
        ]
        run_external_tool(command, "mid3v2")
```

### ✅ CORRECT - Use helper classes for external tool commands:

```python
def test_id3v2_txxx_reading(self):
    from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter

    with temp_file_with_metadata({}, "mp3") as test_file:
        # ✅ Use helper class method - external tool commands belong in helpers
        ID3v2MetadataSetter.set_musicbrainz_trackid_txxx(test_file, track_id)

        result = get_unified_metadata_field(test_file, UnifiedMetadataKey.MUSICBRAINZ_TRACKID)
        assert result == track_id
```

**Rule**: All external tool commands (subprocess calls, tool invocations) must be encapsulated in helper classes in `audiometa.test.helpers`, not in test files. Test files should only call helper class methods.

### ❌ WRONG - Poor test isolation (using library API for setup):

```python
def test_id3v1_genre_reading(self):
    with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
        # ❌ Using our own library to set metadata - poor test isolation
        update_metadata(test_file.path, {
            UnifiedMetadataKey.GENRES_NAMES: ["Rock"]
        }, metadata_format=MetadataFormat.ID3V1)

        # Testing reading - but we used our own writing logic!
        metadata = get_unified_metadata(test_file.path)
        assert metadata.get(UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]
```

### ✅ CORRECT - Use helper classes for proper test isolation:

```python
def test_id3v1_genre_reading(self):
    from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter

    with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
        # ✅ Use helper class to set metadata - proper test isolation
        ID3v1MetadataSetter.set_metadata(test_file.path, {"genre": "Blues"})

        # Now test reading
        metadata = get_unified_metadata(test_file.path)
        assert metadata.get(UnifiedMetadataKey.GENRES_NAMES) == ["Blues"]
```

### ✅ ALTERNATIVE - Use TempFileWithMetadata with specific format:

```python
def test_id3v1_genre_reading(self):
    # ✅ TempFileWithMetadata uses external tools internally
    with TempFileWithMetadata({"genre": "Rock"}, "id3v1") as test_file:
        metadata = get_unified_metadata(test_file.path)
        assert metadata.get(UnifiedMetadataKey.GENRES_NAMES) == ["Rock"]
```

## Test Principle: Only Test the API Function Being Tested

**The rule**: In any test, only use the API function that you're actually testing. Everything else should use helper classes.

### ✅ CORRECT - Deletion tests:

```python
def test_delete_comment_riff(self):
    from audiometa.test.helpers.riff import RIFFMetadataSetter

    with TempFileWithMetadata({}, "wav") as test_file:
        # ✅ Use helper class for setup - not testing setup functionality
        RIFFMetadataSetter.set_comment(test_file.path, "Test comment")
        assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COMMENT) == "Test comment"

        # ✅ Test deletion using library API - this is what we're testing
        update_metadata(test_file.path, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.RIFF)
        assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COMMENT) is None
```

### ✅ CORRECT - Reading tests:

```python
def test_read_comment_riff(self):
    from audiometa.test.helpers.riff import RIFFMetadataSetter

    with TempFileWithMetadata({}, "wav") as test_file:
        # ✅ Use helper class for setup - not testing setup functionality
        RIFFMetadataSetter.set_comment(test_file.path, "Test comment")

        # ✅ Test reading using library API - this is what we're testing
        comment = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COMMENT)
        assert comment == "Test comment"
```

### ✅ CORRECT - Writing tests:

```python
def test_write_comment_riff(self):
    with TempFileWithMetadata({}, "wav") as test_file:
        # ✅ Test writing using library API - this is what we're testing
        update_metadata(test_file.path, {UnifiedMetadataKey.COMMENT: "Test comment"}, metadata_format=MetadataFormat.RIFF)

        # ✅ Use helper class for verification - not testing reading functionality
        comment = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COMMENT)
        assert comment == "Test comment"
```

### ❌ WRONG - Don't mix API functions in tests:

```python
def test_delete_comment_riff(self):
    with TempFileWithMetadata({}, "wav") as test_file:
        # ❌ Using library API for setup when testing deletion
        update_metadata(test_file.path, {UnifiedMetadataKey.COMMENT: "Test comment"}, metadata_format=MetadataFormat.RIFF)

        # ✅ This is correct - testing deletion
        update_metadata(test_file.path, {UnifiedMetadataKey.COMMENT: None}, metadata_format=MetadataFormat.RIFF)
        assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.COMMENT) is None
```

## Individual Metadata Reading Tests

### Use get_unified_metadata_field for Single Metadata Field Tests

When testing reading of a **single metadata field**, use `get_unified_metadata_field()` instead of `get_unified_metadata()` for better performance and clarity.

### ❌ WRONG - Inefficient for single field:

```python
def test_title_reading(self, test_file):
    metadata = get_unified_metadata(test_file.path)
    title = metadata.get(UnifiedMetadataKey.TITLE)
    assert title == "Expected Title"
```

### ✅ CORRECT - Use get_unified_metadata_field:

```python
def test_title_reading(self, test_file):
    title = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TITLE)
    assert title == "Expected Title"
```

### When to Use Each Function

- **`get_unified_metadata_field()`**: When testing a single metadata field
- **`get_unified_metadata()`**: When testing multiple metadata fields or full metadata workflows
