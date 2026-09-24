# Development Guidelines

This document outlines the coding standards and best practices for developing this project.

Organization-wide Python tooling, CI patterns, and shared style (including [string enums](https://github.com/BehindTheMusicTree/python-project-standards/blob/main/docs/string-enums.md)) are summarized in **[BehindTheMusicTree/python-project-standards — Development baseline](https://github.com/BehindTheMusicTree/python-project-standards/blob/main/docs/development.md)**. This library delegates **lint** to org **`reusable-pre-commit.yml`** (**`@v4.3.2`**, matching root [`STANDARDS_VERSION`](STANDARDS_VERSION)) and runs **tests** in [`.github/workflows/lint-and-test.yml`](.github/workflows/lint-and-test.yml) (matrix, markers, coverage—see upstream [CHANGELOG](https://github.com/BehindTheMusicTree/python-project-standards/blob/main/CHANGELOG.md) for removal of **`reusable-test-matrix`** in v3). Ruff/Mypy baselines are vendored under **`baselines/`** (`ruff.toml`, **`DIGESTS`**, **`expected-mypy.json`**) per [migration-guide](https://github.com/BehindTheMusicTree/python-project-standards/blob/main/docs/migration-guide.md); **`scripts/verify-standards.sh`** runs **`check_lint_baseline.py`** to enforce them. When upgrading standards, refresh **`baselines/`** and scripts from the release tag, bump the **`uses:`** pin and **`STANDARDS_VERSION`** together, then read [versioning](https://github.com/BehindTheMusicTree/python-project-standards/blob/main/docs/versioning.md).

## Table of Contents

- [Code Quality](#code-quality)
  - [General Practices](#general-practices)
  - [Code Style Conventions](#code-style-conventions)
    - [Module Naming](#module-naming)
  - [Docstrings](#docstrings)
    - [Docstring Format](#docstring-format)
    - [When to Add Docstrings](#when-to-add-docstrings)
    - [When NOT to Add Docstrings](#when-not-to-add-docstrings)
  - [Type Checking](#type-checking)
  - [Known Linting Issues](#known-linting-issues)
    - [Ruff F823 False Positive](#ruff-f823-false-positive)
- [Project Documentation](#project-documentation)
  - [Documentation Files](#documentation-files)
  - [Changelog and `[Unreleased]`](#changelog-and-unreleased)

## Code Quality

### General Practices

Follow these code quality standards when developing:

- **Remove commented-out code** - Don't leave commented-out code in the codebase. If code is no longer needed, remove it. Use version control (git) to recover old code if needed.
- **No hardcoded credentials, API keys, or secrets** - Never commit credentials, API keys, passwords, or other sensitive information to the repository. Use environment variables or secure configuration management instead.
- **Run pre-commit hooks** - Always run `pre-commit run --all-files` before committing. This includes **`verify-python-project-standards`** ([`scripts/verify-standards.sh`](scripts/verify-standards.sh): layout, ruff/mypy in config, CI references org reusables, **`STANDARDS_VERSION`** vs **`@v…`** pins, **`baselines/`** digest and overlay rules via **`check_lint_baseline.py`**), linting, formatting, type checking, assert statement checks, debug statement detection, and other quality checks. Pre-commit hooks are automatically enforced, but running them manually helps catch issues early.

**Note:** Pre-commit hooks are configured to use tools from your active Python environment. Always activate the project's virtual environment (`.venv`) before running git commits. See the [Virtual Environment](.claude/rules/virtual-environment.md) rules for details.

### Code Style Conventions

#### Module Naming

All Python module files must follow PEP 8 naming conventions:

- **Use `snake_case` for module names**: Module files should use lowercase with underscores

  - ✅ Good: `metadata_format.py`, `unified_metadata_key.py`, `id3v1_raw_metadata.py`
  - ❌ Bad: `MetadataFormat.py`, `UnifiedMetadataKey.py`, `Id3v1RawMetadata.py`

- **Private modules can start with `_`**: Internal/private modules that are not part of the public API can use a leading underscore prefix

  - ✅ Good: `_MetadataManager.py`, `_Id3v2Manager.py`, `_audio_file.py`
  - These indicate internal implementation details and are not imported by external users

- **Class names remain PascalCase**: While module files use `snake_case`, the classes they contain still follow Python conventions (PascalCase)
  - Example: `metadata_format.py` contains the `MetadataFormat` class
  - Example: `unified_metadata_key.py` contains the `UnifiedMetadataKey` enum

**Why this matters:**

- PEP 8 compliance ensures consistency across the codebase
- `snake_case` module names are the Python standard and improve readability
- Leading `_` prefix signals private/internal modules to other developers
- Consistent naming makes the codebase easier to navigate and understand

**Note:** The `N999` linting rule (invalid module name) is configured to ignore modules starting with `_` since these are intentionally private. However, all public modules must use `snake_case`.

### Docstrings

Docstrings should only be added when they provide value (complex logic, public API, edge cases, etc.). When docstrings are needed, use a **systematic Google-style format** for consistency.

#### Docstring Format

When docstrings are needed (for public API, complex logic, etc.), use a **systematic Google-style format** for consistency:

```python
def public_api_function(param1: str, param2: int | None = None) -> dict[str, Any]:
    """Brief one-line description.

    More detailed explanation if needed. Can span multiple lines
    to explain complex behavior, edge cases, or important details.

    Args:
        param1: Description of param1
        param2: Description of param2. Defaults to None.

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
        FileNotFoundError: When file doesn't exist

    Examples:
        >>> result = public_api_function("test", 42)
        >>> print(result)
        {'key': 'value'}
    """
    # Implementation
```

#### When to Add Docstrings

- Public API functions/classes (exported from `__init__.py`)
- Complex business logic that isn't obvious
- Functions with non-obvious side effects
- Important edge cases or assumptions

#### When NOT to Add Docstrings

- Simple getter/setter functions
- Self-explanatory functions with descriptive names
- Test functions (unless testing complex scenarios)
- Internal helper functions that are obvious from context

### Type Checking

- **Production code** (`audiometa/` excluding `audiometa/test/`): Strict type checking

  - All functions must have type annotations
  - No untyped function definitions
  - Strict type compatibility checks
  - Missing type stubs for external libraries are handled via mypy overrides in `pyproject.toml` (e.g., `mutagen.*`, `pytest`)
  - **Note**: Do not add `# type: ignore[import-not-found]` comments for libraries that already have mypy overrides configured, as mypy will report them as unused

- **Test code** (`audiometa/test/`): Relaxed type checking
  - Functions can be untyped (no type annotations required)
  - Missing type annotations for variables are allowed
  - This allows test code to be more flexible while maintaining type safety in production code
  - **Note on pytest type stubs**: Mypy will report "Cannot find implementation or library stub for module named 'pytest'" because pytest type stubs are not available as a separate package. This is expected and acceptable - real import errors are still caught by test execution at runtime. The mypy overrides in `pyproject.toml` relax type checking rules for test files to accommodate this.

**Note:** Type checking is automatically enforced via pre-commit hooks and CI/CD. See the [Committing](CONTRIBUTING.md#5-committing) section in CONTRIBUTING.md for details on pre-commit hooks.

### Known Linting Issues

#### Ruff F823 False Positive

Ruff may incorrectly report `F823: Local variable referenced before assignment` when an imported exception class is:

1. Referenced in a docstring's `Raises:` section
2. Used later in the code with `raise`

This is a known limitation of ruff's static analysis. When this occurs, it's acceptable to suppress the false positive with `# noqa: F823` on the line where the exception is raised.

Example:

```python
from ...exceptions import MetadataFieldNotSupportedByMetadataFormatError

def some_function():
    """Do something.

    Raises:
        MetadataFieldNotSupportedByMetadataFormatError: If field not supported
    """
    if condition:
        raise MetadataFieldNotSupportedByMetadataFormatError("message")  # noqa: F823
```

## Project Documentation

### Documentation Files

When making changes to the codebase, ensure relevant documentation is updated:

- **README.md**: Update when adding new features, changing behavior, or modifying installation/usage instructions
- **CHANGELOG.md**: Always update `## [Unreleased]` in the **same PR** as the code ([Changelog and `[Unreleased]`](#changelog-and-unreleased); [Changelog Best Practices](CHANGELOG.md#changelog-best-practices); `.claude/rules/changelog.md`)
- **DEVELOPMENT.md**: Update when changing development standards or adding new guidelines
- **CONTRIBUTING.md**: Update when changing development workflow (primarily for maintainers; contributors may update in exceptional cases, e.g., when adding hooks for new features in other languages)
- **docs/**: Update relevant documentation files in the `docs/` directory when adding features or changing behavior that affects user-facing functionality

**Note:** Documentation should be updated as part of the same PR that introduces the changes, not as a separate follow-up PR.

### Changelog and `[Unreleased]`

Edit `CHANGELOG.md` under `## [Unreleased]` whenever your change affects **users, integrators, or the public surface** (library API exported from `audiometa`, CLI behavior or flags, default behavior, or response shapes). Use the usual categories (Added, Changed, Fixed, etc.); see [Changelog Best Practices](CHANGELOG.md#changelog-best-practices).

- **Same PR as the code** — Do not merge user-visible changes with an empty or stale `[Unreleased]` section.
- **What usually needs an entry** — New or changed public symbols, CLI changes, user-visible bug fixes, breaking changes (document clearly).
- **What often does not** — Internal refactors with identical external behavior; test-only work that does not fix a user-visible bug (mention tests under the related feature or fix if there is one).
- **Before you open or finalize a PR** — Re-read `## [Unreleased]` and confirm it matches the diff.
- **After editing `CHANGELOG.md`** — Run `python scripts/verify_changelog.py` so section order matches `scripts/prepare_release.py` (see `.claude/rules/changelog.md`, **CHANGELOG.md structure and integrity**).

Agents also follow `.claude/rules/changelog.md` and [AGENTS.md](AGENTS.md#changelog).
