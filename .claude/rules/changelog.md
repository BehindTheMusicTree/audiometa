# Changelog Best Practices

## General Principles

- Changelogs are for humans, not machines.
- Include an entry for every version, with the latest first.
- Group similar changes under: Added, Changed, Improved, Deprecated, Removed, Fixed, Documentation, Performance, CI.
- **"Test" is NOT a valid changelog category** - tests should be mentioned within the related feature or fix entry, not as standalone entries.
- Use an "Unreleased" section for upcoming changes.
- Follow Semantic Versioning where possible.
- Use ISO 8601 date format: YYYY-MM-DD.
- Avoid dumping raw git logs; summarize notable changes clearly.

## `CHANGELOG.md` structure and integrity

**Required layout** (outside fenced code blocks; markdown examples inside ` ``` ` fences in `CHANGELOG.md` must not use real `## [version]` headers that duplicate the live sections):

1. Exactly **one** `## [Unreleased]` heading.
2. **Immediately after** the `[Unreleased]` notes, the next section must be the newest release: `## [X.Y.Z] - YYYY-MM-DD`.
3. **Older releases** follow in **strictly decreasing** semantic order (e.g. `1.4.1`, then `1.4.0`, then `1.3.3`).

This matches `scripts/prepare_release.py`, which replaces the `[Unreleased]` block and inserts the new version **between** `[Unreleased]` and the first `## [X.Y.Z] - date` below it. If older versions sit above `[Unreleased]` or order is wrong, the file reads incorrectly and releases can produce the wrong section order.

**Whenever you edit `CHANGELOG.md`** (including moving release notes or cutting a release by hand), verify before committing or running `prepare_release.py`:

```bash
python scripts/verify_changelog.py
```

Fix reported issues until the script prints `CHANGELOG.md OK`. Agents should run this after substantive changelog edits, not only rely on visual skim.

## Keeping `[Unreleased]` aligned with code changes

**Whenever you modify the codebase in ways that matter to users or integrators**, update `CHANGELOG.md` under `## [Unreleased]` in the **same** PR or change series as the code. Do not ship behavioral, API, or CLI changes with an empty or outdated `[Unreleased]` section.

**Add or adjust `[Unreleased]` entries when you:**

- Add, change, or remove **public API** (symbols exported from `audiometa`, CLI commands, flags, or documented behavior)
- Fix a **user-visible** bug in the library or CLI
- Change **defaults** or **response shapes** (e.g. new top-level keys from `get_full_metadata`, new required fields)
- Introduce **breaking changes** (document clearly; follow repo conventions for severity)

**Usually skip a new changelog bullet** when the change is strictly internal (refactor with identical external behavior, private helpers only). **Test-only** changes that do not fix a user-visible bug typically do not need their own entry; mention tests under the related feature or fix if applicable.

**Before you treat a coding task as complete:** Open `CHANGELOG.md`, read `## [Unreleased]`, and confirm it still describes the current diff. If the code moved on (new API, behavior change, fix), **edit `[Unreleased]`** so it stays accurate. If you changed `CHANGELOG.md`, run `python scripts/verify_changelog.py` and fix failures before finishing.

**Human-readable summary:** [DEVELOPMENT.md — Changelog and `[Unreleased]`](DEVELOPMENT.md#changelog-and-unreleased).

## Release Process

**IMPORTANT: All releases must follow the steps documented in `CONTRIBUTING.md`.**

**CRITICAL: Releases must be prepared on the `main` branch.** Before starting the release process, ensure you are on the `main` branch and that it is up to date with the remote:

```bash
git checkout main
git pull origin main
```

Before preparing a release, refer to the "Releasing _(For Maintainers)_" section in `CONTRIBUTING.md` for the complete release process. The release process includes:

1. **Ensuring you're on the `main` branch** - Releases must be prepared from `main`, not from feature branches
2. Checking `TODO.md` for critical items
3. Reviewing the `[Unreleased]` section in `CHANGELOG.md`
4. Running `python scripts/verify_changelog.py` (layout must match `prepare_release.py`; see **CHANGELOG.md structure and integrity** above)
5. Running `scripts/prepare_release.py` (updates CHANGELOG with version and date, bumps version, commits, and tags)
6. Pushing main and the new tag
7. CI/CD will automatically handle PyPI publishing

**Do not skip any steps in the release process.** See `CONTRIBUTING.md` for detailed instructions.

## Test Coverage in Changelog

**Tests should NOT be listed separately in the "Added" section.**

Tests are implementation details that support features or fixes. They should be mentioned within the related feature or fix entry, not as standalone entries.

### ❌ WRONG - Separate test entry:

```markdown
### Fixed

- **Bug Fix**: Fixed issue with metadata parsing

### Added

- **Tests**: Added comprehensive unit tests for metadata parsing
```

### ✅ CORRECT - Tests mentioned with the feature/fix:

```markdown
### Fixed

- **Bug Fix**: Fixed issue with metadata parsing
  - Includes comprehensive unit tests covering edge cases and error scenarios
```

### ✅ CORRECT - Tests mentioned inline:

```markdown
### Fixed

- **Mutagen Exception Handling**: Added comprehensive exception handling for mutagen operations:
  - Created `_handle_mutagen_exception()` helper function to centralize exception handling
  - Includes comprehensive unit tests (21 test cases) covering all exception handling scenarios
```

## Documentation Entries

**Documentation changes should be listed in the "Documentation" section, not "Added" or "Improved".**

Documentation-only changes (new guides, documentation updates, README changes, etc.) should be categorized under "Documentation" to clearly distinguish them from code changes.

### ✅ CORRECT - Documentation in Documentation section:

```markdown
### Documentation

- **Metadata Formats Guide**: Added comprehensive `METADATA_FORMATS.md` guide documenting all supported metadata formats
- **Metadata Field Guide**: Enhanced `METADATA_FIELD_GUIDE.md` with BWF field support
```

### ❌ WRONG - Documentation in Added section:

```markdown
### Added

- **Metadata Formats Guide**: Added comprehensive `METADATA_FORMATS.md` guide
```

### When to Use Documentation Section

- New documentation files (guides, tutorials, API docs)
- Updates to existing documentation
- README changes
- Documentation structure improvements
- Clarifications and corrections to documentation

### When NOT to Use Documentation Section

- Code changes that happen to include documentation updates (use "Added", "Fixed", etc.)
- Docstring updates that are part of code changes (mention in the code change entry)

## When to Mention Tests

- **Mention tests** when they provide important context about the change (e.g., "includes tests covering edge cases")
- **Don't create separate entries** for tests unless they represent a significant testing infrastructure improvement (e.g., new test framework, new test utilities)
- **Test infrastructure changes** (new test helpers, test framework updates) can be mentioned in "Improved" or "Added" sections, but test coverage for features/fixes should be mentioned with the feature/fix

## Examples

### Feature with Tests

```markdown
### Added

- **New Feature**: Added support for FLAC metadata reading
  - Includes comprehensive unit tests covering various metadata formats
  - Includes integration tests verifying compatibility with external tools
```

### Bug Fix with Tests

```markdown
### Fixed

- **Metadata Parsing**: Fixed issue with parsing ID3v2 tags containing special characters
  - Includes regression tests to prevent future occurrences
```

### Test Infrastructure (Can be separate)

```markdown
### Improved

- **Test Infrastructure**: Added new test helper utilities for creating temporary audio files
  - Simplifies test setup and improves test maintainability
```
