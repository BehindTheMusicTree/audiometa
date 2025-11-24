# Commit Message Guide

This guide explains how to write commit messages for this project. We follow a structured commit format inspired by [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) to keep the commit history readable, support automatic changelog generation, and ensure consistent release versioning.

## Table of Contents

- [Before Committing](#before-committing)
  - [Virtual Environment](#virtual-environment)
  - [Pre-commit Hooks](#pre-commit-hooks)
- [Commit Message Format](#commit-message-format)
  - [Format Structure](#format-structure)
  - [Breaking Changes](#breaking-changes)
- [Commit Types](#commit-types)
- [Scopes](#scopes)
  - [Common Scopes](#common-scopes)
  - [Test Commits Best Practices](#test-commits-best-practices)
- [Examples](#examples)
- [Guidelines](#guidelines)

## Before Committing

### Virtual Environment

**IMPORTANT:** Always activate the project's virtual environment (`.venv`) before running git commits. Pre-commit hooks use `language: system` and require the correct Python environment.

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate    # Windows

# Verify you're in the virtual environment
which python3  # Should point to .venv/bin/python3
```

**Why this matters:**

- Pre-commit hooks use tools from your active Python environment
- Without an activated virtual environment, tools may use system-installed versions with incorrect Python interpreters or missing dependencies
- This can cause pre-commit hooks to fail (e.g., mypy failing due to missing Python 3.12 interpreter)

### Pre-commit Hooks

All code must pass pre-commit hooks before committing. These hooks automatically run when you commit and include:

- **Code formatting**: trailing-whitespace, isort, ruff-format, pydocstringformatter, ruff
- **Type checking**: mypy
- **Linting**: ruff (replaces autoflake and flake8)
- **Assert statement check**: Custom hook that fails if assert statements are found in production code
- **Debug statement detection**: Checks for debug statements in production code
- **System dependency version verification**: Ensures installed system dependencies match pinned versions

**Run pre-commit hooks manually before committing:**

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run hooks on staged files only (default when committing)
pre-commit run
```

**Note:** Ruff handles unused imports/variables (replaces autoflake) and most linting rules (replaces flake8). The trailing-whitespace hook automatically removes trailing whitespace without failing. Ruff-format handles code formatting and EOF newlines automatically.

**If hooks fail:**

1. Fix the issues reported by the hooks
2. Re-run `pre-commit run --all-files` to verify fixes
3. Stage your changes and commit again

## Commit Message Format

### Format Structure

```
<type>(<optional scope>): <short summary>

[optional body]

[optional footer]
```

**Components:**

- **Type**: Required. Describes the kind of change (see [Commit Types](#commit-types))
- **Scope**: Optional. Clarifies which part of the library is affected (see [Scopes](#scopes))
- **Summary**: Required. Brief description in imperative mood, under 72 characters
- **Body**: Optional. Detailed explanation of the change
- **Footer**: Optional. Used for breaking changes or issue references

### Breaking Changes

For breaking changes, append `!` after the type/scope:

```
<type>(<optional scope>)!: <short summary>
```

Or include a `BREAKING CHANGE:` footer in the commit body:

```
feat(core): update metadata interface

BREAKING CHANGE: The get_metadata function has been removed.
Use get_unified_metadata instead.
```

## Commit Types

| Type     | Description                                          |
| -------- | ---------------------------------------------------- |
| feat     | A new feature or enhancement                         |
| fix      | A bug fix                                            |
| refactor | Code refactoring that doesn't change behavior        |
| docs     | Documentation-only changes                           |
| test     | Adding or updating tests                             |
| chore    | Maintenance tasks (e.g. CI, packaging, dependencies) |
| style    | Code style or formatting changes (no logic impact)   |
| perf     | Performance improvements                             |

## Scopes

Use a scope to clarify which part of the library your change affects. Scopes are optional but encouraged for clarity.

### Common Scopes

| Scope  | Example                                     | Description                  |
| ------ | ------------------------------------------- | ---------------------------- |
| core   | refactor(core): simplify metadata interface | Core metadata handling logic |
| id3v1  | fix(id3v1): handle encoding issues          | ID3v1 tag format             |
| id3v2  | feat(id3v2): add custom text frame support  | ID3v2 tag format             |
| vorbis | fix(vorbis): improve comment parsing        | Vorbis comment format        |
| riff   | feat(riff): detect and write INFO chunks    | RIFF metadata format         |
| test   | refactor(test): reorganize test fixtures    | Testing infrastructure       |
| deps   | chore(deps): update mutagen dependency      | Dependency management        |
| docs   | docs: improve README example                | Documentation updates        |

### Test Commits Best Practices

For a single library project, use `test:` as the **type**, not the scope, for general test changes:

- `test(mp3): add roundtrip test for title tag`
- `test(core): improve coverage for metadata merge`

Reserve `chore(test):`, `refactor(test):` for test infrastructure changes:

- `chore(test): reorganize test helpers`
- `refactor(test): improve test fixture structure`

**Summary:**

| Use case                        | Best practice                             |
| ------------------------------- | ----------------------------------------- |
| Adding or improving tests       | `test(scope): …`                          |
| Fixing a bug in a test          | `fix(test): …` or `test(scope): fix …`    |
| Changing test utilities/config  | `chore(test): …`                          |
| Refactoring core test structure | `refactor(test): …`                       |
| Feature/bug in main code        | Use relevant scope (e.g., `feat(mp3): …`) |

## Examples

### Feature

```
feat(id3v2): add album artist tag support
```

### Bug Fix

```
fix(vorbis): correctly parse embedded picture metadata
```

### Refactoring

```
refactor(core): move format detection to utils module
```

### Test

```
test(mp3): add roundtrip test for metadata write/read
```

### Documentation

```
docs: document supported tag fields
```

### Maintenance

```
chore(deps): bump mutagen to 1.47.0
```

### Breaking Change

```
feat(core)!: remove deprecated get_metadata function

BREAKING CHANGE: The get_metadata function has been removed.
Use get_unified_metadata instead.
```

### With Body

```
feat(mp3): support writing composer tag

Added support for writing the "composer" field in ID3v2.4 MP3 files.
Ensures backward compatibility with ID3v2.3 readers.
```

## Guidelines

- **Use imperative mood**: "add", "fix", not "added", "fixed"
- **Keep summary under 72 characters**: Ensures readability in git log
- **Use commit body for context**: Provide additional details when needed
- **One logical change per commit**: Each commit should represent a single, complete change
- **Small, focused commits**: Better than large, mixed commits
- **Write clear summaries**: The summary should clearly describe what the commit does
- **Reference issues when applicable**: Use "Fixes #123" or "Closes #456" in the footer

**Good commit examples:**

- ✅ `fix(id3v1): handle encoding issues with special characters`
- ✅ `feat(vorbis): add support for custom comment fields`
- ✅ `test(mp3): add regression test for title tag corruption`

**Bad commit examples:**

- ❌ `fixed bug` (too vague, no type/scope)
- ❌ `feat: added new feature` (not descriptive)
- ❌ `WIP: working on stuff` (not following format)
- ❌ `fix: fixed the thing that was broken` (redundant, not imperative)
