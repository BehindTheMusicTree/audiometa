# TODO

This file tracks future work, improvements, and testing tasks for AudioMeta Python.

**Note for Contributors**: This TODO list is maintained by project maintainers. If you'd like to suggest a new task or work on an existing one, please open a GitHub issue first for discussion. Maintainers will update this file based on project priorities and community feedback.

## Rating Profile Compatibility Testing

### High Priority

- [ ] **Test rating profile compatibility across different audio players**
  - Verify which rating values are actually readable and display correctly
  - Test Profile A (255 non-proportional) with Windows Media Player, MusicBee, Winamp, kid3
  - Test Profile B (100 proportional) with FLAC players and Vorbis-compatible software
  - Test Profile C (255 proportional) with Traktor Pro and Traktor DJ

- [ ] **Support of non-supported fields**
  - Add support for metadata fields that are currently not handled by the library

## Feature Enhancements

### Medium Priority

- [ ] **Implement synchronized lyrics support in future versions**
  - Add support for SYLT (Synchronized Lyrics/Text) frames in ID3v2
  - Implement time-stamped lyrics for karaoke and synchronized text display
  - Support multiple synchronized lyrics entries with different languages

- [ ] **Implement full multi-language unsynchronized lyrics support in future versions**
  - Extend USLT (Unsynchronized Lyrics) frame support for multiple languages
  - Add language code handling (ISO 639-2) for lyrics and other text fields
  - Support multiple lyrics entries in different languages within the same file

- [ ] **OGG file support**
  - Currently planned but not implemented
  - Vorbis comment support for OGG files
  - Integration with existing Vorbis manager

- [ ] **Batch processing with parallelization**
  - Add Python API functions for processing multiple audio files (CLI already supports this)
  - Bridge the gap between CLI multi-file support and single-file Python API
  - Implement parallel metadata reading/writing operations for better performance
  - Add progress tracking and consolidated error handling for batch operations
  - Consider thread pool or multiprocessing for CPU-intensive tasks
  - Provide both sequential and parallel processing options

- [ ] **Check multi-value separators compatibility with standard metadata readers**
  - Current implementation uses prioritized separators: "//", "\\\\", "\\", ";", "/", "," for joining multi-value fields
  - Smart parsing logic applies when null separators (\\x00) are present (always parse) or for single entries without nulls (legacy data detection)
  - Test compatibility with standard readers like iTunes, VLC, Windows Media Player to ensure correct parsing of multi-value metadata

- [ ] **Check compliance with each format's max length limitations with adapted exceptions and tests**
  - Verify ID3v1 (fixed sizes: e.g., title 30 bytes, artist 30 bytes), ID3v2 (variable but practical limits), RIFF, and Vorbis format constraints
  - Implement or adapt exceptions for length violations
  - Add unit and integration tests to validate length enforcement and error handling

- [ ] **Provide a Docker image**
  - Create a Dockerfile for the project
  - Set up containerized environment for easy deployment and testing
  - Include necessary dependencies and entry points

- [ ] **Broadcast Wave Format (BWF) support**
  - Implement reading and writing of BWF metadata for WAV files
  - Extend RIFF manager or create dedicated BWF manager
  - Add support for BWF-specific fields like time reference, originator, etc.

- [ ] **Take a look at ID3v2.0 and ID3v2.2 and test it**
  - Review and test support for ID3v2.0 and ID3v2.2 frame handling and version-specific features

---

## Infrastructure & Publishing

### High Priority

- [ ] **Set up CI workflow for automatic PyPI publishing**
  - Configure GitHub Actions workflow to publish to PyPI on releases/tags
  - Set up PyPI API token as GitHub secret
  - Test publishing process
  - Document release process

- [ ] **Add PyPI-related badges to README**
  - PyPI version badge
  - PyPI downloads badge
  - Update badges section with PyPI links

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

## Contributing

If you'd like to work on any of these items:

1. Check if there's already an open issue for the task
2. Create a new issue if needed
3. Fork the repository and create a feature branch
4. Implement your changes with appropriate tests
5. Submit a pull request

For questions about specific tasks, please open an issue for discussion.
