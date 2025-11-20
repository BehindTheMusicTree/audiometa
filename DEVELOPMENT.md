# Development Guidelines

This document outlines the coding standards and best practices for developing this project.

## Table of Contents

- [Code Style Conventions](#code-style-conventions)
  - [Module Naming](#module-naming)
- [Type Checking](#type-checking)
  - [Type Checking Rules](#type-checking-rules)
- [Known Linting Issues](#known-linting-issues)
  - [Ruff F823 False Positive](#ruff-f823-false-positive)

## Code Style Conventions

### Module Naming

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

## Type Checking

### Type Checking Rules

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

## Known Linting Issues

### Ruff F823 False Positive

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
