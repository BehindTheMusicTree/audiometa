# 🧭 Contributing Guidelines

Thank you for your interest in contributing!
This project is currently maintained by a solo developer, but contributions, suggestions, and improvements are welcome.

## Table of Contents

- [🧑‍🤝‍🧑 Contributors vs Maintainers](#-contributors-vs-maintainers)
- [💻 Contributing Code](#-contributing-code)
- [📦 Environment Setup](#-environment-setup)
- [🧱 Development Workflow](#-development-workflow)
  - [Main Branch (`main`)](#main-branch-main)
  - [Feature Branches (`feature/<name>`)](#feature-branches-featurename)
  - [Hotfix Branches (`hotfix/<issue>`)](#hotfix-branches-hotfixissue)
  - [🧪 Testing](#-testing)
    - [Run Local Tests](#run-local-tests)
    - [Run Coverage](#run-coverage)
      - [Running Tests with Coverage](#running-tests-with-coverage)
      - [Running Tests Without Coverage](#running-tests-without-coverage)
      - [Viewing Coverage Reports](#viewing-coverage-reports)
    - [Lint Code for Style Consistency](#lint-code-for-style-consistency)
  - [📝 Commit Message Convention](#-commit-message-convention)
  - [✅ Pre-PR / Pre-Merge Checklist](#-pre-pr--pre-merge-checklist)
  - [🚀 Releasing _(For Maintainers)_](#releasing-for-maintainers)
- [🪪 License & Attribution](#-license--attribution)
- [🌍 Contact & Discussions](#-contact--discussions)

## Contributors vs Maintainers

**Contributors**

Anyone can be a contributor by:

- Submitting bug reports or feature requests via GitHub Issues
- Proposing code changes through Pull Requests
- Improving documentation
- Participating in discussions
- Testing and providing feedback

**Maintainers**

The maintainer(s) are responsible for:

- Reviewing and merging Pull Requests
- Managing releases and versioning
- Ensuring code quality and project direction
- Responding to critical issues
- Maintaining the project's infrastructure
- Creating and managing hotfix branches for urgent production fixes
- Updating the changelog (contributors should not modify `CHANGELOG.md`)

_Note: Contributors can submit fixes for critical issues via feature branches. Maintainers may promote these to hotfix branches when urgent production fixes are needed._

Currently, this project has a solo maintainer, but the role may expand as the project grows.

## 💡 Contributing Code

1. Fork the repository
2. Create a `feature/` branch
3. Run tests locally
4. Open a Pull Request with a clear description

## 📦 Environment Setup

Ensure you're using:

- Python 3.10 or higher
- Virtual environment with dependencies:

  ```bash
  python -m venv .venv
  source .venv/bin/activate  # (Linux/macOS)
  .venv\Scripts\activate     # (Windows)
  pip install -e ".[dev]"
  ```

## 🧱 Development Workflow

We follow a light GitFlow model adapted for small teams and open-source projects:

### Main Branch (`main`)

- The stable, always-deployable branch
- All tests must pass before merging
- Releases are tagged from `main`

### Feature Branches (`feature/<name>`)

- Create one for each new feature or bug fix
- Example:
  ```bash
  git checkout -b feature/improve-genre-classification
  ```
- Merge into `main` via Pull Request when complete and tested

### Hotfix Branches (`hotfix/<issue>`) _(For Maintainers)_

- For urgent bug fixes on production versions
- Contributors can submit fixes via feature branches that maintainers may promote to hotfixes if needed

### 📝 Commit Message Convention

We follow a structured commit format inspired by [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
This helps keep the commit history readable, supports automatic changelog generation, and ensures consistent release versioning.

#### Format

<type>(<optional scope>): <short summary>

[optional body]

##### Breaking Changes

For breaking changes, append `!` after the type/scope:

<type>(<optional scope>)!: <short summary>

Or include a `BREAKING CHANGE:` footer in the commit body.

#### Example

feat(mp3): support writing composer tag

Added support for writing the "composer" field in ID3v2.4 MP3 files.
Ensures backward compatibility with ID3v2.3 readers.

#### Allowed Commit Types

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

#### Scopes

Use a scope to clarify which part of the library your change affects.
Scopes are optional but encouraged for clarity.

##### Common Scopes

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

##### Test Commits Best Practices

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

#### Examples

feat(id3v2): add album artist tag support
fix(vorbis): correctly parse embedded picture metadata
refactor(core): move format detection to utils module
test(mp3): add roundtrip test for metadata write/read
docs: document supported tag fields
chore(deps): bump mutagen to 1.47.0
feat(core)!: remove deprecated get_metadata function

BREAKING CHANGE: The get_metadata function has been removed.
Use get_unified_metadata instead.

#### Guidelines

Use imperative mood ("add", "fix", not "added", "fixed").

Keep the summary under 72 characters.

Use the commit body for additional context if needed.

One logical change per commit.

Small, focused commits are better than large, mixed ones.

### 🧪 Testing

We use pytest for all automated testing with markers for unit, integration, and e2e tests.

#### Quick Reference

```bash
# Run all tests
pytest

# Run tests by category (matches CI behavior)
pytest -m unit          # Fast unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e           # End-to-end tests only

# Run without slow e2e tests
pytest -m "not e2e"

# Run with coverage (recommended before committing)
pytest --cov=audiometa --cov-report=html --cov-report=term-missing --cov-fail-under=85
```

**Note:** CI runs tests separately by marker (`unit`, `integration`, `e2e`) with coverage. The coverage threshold of 85% applies to the combined total.

**Note:** CI tests only run on latest OS versions: `ubuntu-latest`, `macos-latest`, `windows-latest`.

For detailed test documentation, including test principles, markers, and advanced usage, see [`audiometa/test/README.md`](test/README.md).

#### Lint Code for Style Consistency

We use [pre-commit](https://pre-commit.com/) hooks to automatically check code quality before commits.

**First-time setup:**

```bash
# Install pre-commit (if not already installed)
pip install -e ".[dev]"

# Install the git hooks
pre-commit install
```

**Usage:**

Once installed, pre-commit will automatically run on every commit. You can also run it manually:

```bash
# Run on all files
pre-commit run --all-files

# Run only on staged files (default when committing)
pre-commit run
```

**Auto-fix formatting:**

Pre-commit will auto-fix black, isort, and docformatter issues. You can also run manually:

```bash
black . && isort . && docformatter --in-place --wrap-summaries=120 --wrap-descriptions=120 --make-summary-multi-line .
```

Note: `mypy` and `flake8` require manual fixes as they don't auto-format.

**Pre-commit hooks include (in execution order):**

1. **autoflake**: Removes unused imports and variables from Python files
2. **isort**: Sorts and organizes import statements according to PEP 8
3. **ruff-format**: Formats Python code (replaces black) - handles code formatting but not comments/docstrings
4. **docformatter**: Formats docstrings (triple-quoted strings) according to PEP 257
5. **fix-long-comments**: Custom hook that automatically wraps long comment lines (starting with `#`) to fit within 120 characters
6. **ruff**: Auto-fixes linting issues (code style, unused variables, etc.) - does not fix line length violations
7. **mypy**: Static type checking - reports type errors but does not auto-fix
8. **flake8**: Lints code for style issues (PEP 8 compliance) - reports errors but does not auto-fix
9. **Assert check**: Custom hook that prevents `assert` statements in production code (use proper exceptions instead)

**Known Linting Issues:**

- **Ruff F823 False Positive**: Ruff may incorrectly report `F823: Local variable referenced before assignment` when an imported exception class is:

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

**Type Checking Behavior:**

- **Pre-commit hooks**: `mypy` checks staged files with `--follow-imports=normal`, which means:
  - Staged files are checked along with their imports
  - This ensures type consistency across the codebase
  - Errors in imported files (even if unstaged) will block your commit
  - **Exception for large refactorings**: For very large commits (e.g., major refactorings), you can temporarily use `--follow-imports=skip` in `.pre-commit-config.yaml` to allow incremental commits, but this should be reverted immediately after the refactoring is complete
- **CI/CD**: `mypy` checks the **entire codebase** to ensure type consistency across all files

**Type Checking Rules:**

- **Production code** (`audiometa/` excluding `audiometa/test/`): Strict type checking

  - All functions must have type annotations
  - No untyped function definitions
  - Strict type compatibility checks
  - Missing type stubs for external libraries are ignored with `# type: ignore[import-not-found]`

- **Test code** (`audiometa/test/`): Relaxed type checking
  - Functions can be untyped (no type annotations required)
  - Missing type annotations for variables are allowed
  - This allows test code to be more flexible while maintaining type safety in production code

This means:

- You can commit individual files even if other files have type errors
- Before opening a PR, run `pre-commit run --all-files` or `mypy audiometa` to check the entire codebase
- CI will catch any type errors in the full codebase before merging
- Test code type errors are acceptable as long as they don't prevent tests from running

CI will automatically test all pushes and PRs using GitHub Actions.

### ✅ Pre-PR / Pre-Merge Checklist

Before submitting a Pull Request (contributors) or merging to `main` (maintainers), ensure the following checks are completed:

#### For Contributors (Before Opening a PR)

**1. Code Quality Checks**

- ✅ Run pre-commit hooks: `pre-commit run --all-files`
- ✅ All linting checks pass (black, isort, docformatter, mypy, flake8)
- ✅ Code is properly formatted

**2. Tests**

- ✅ All tests pass: `pytest`
- ✅ Coverage meets threshold (≥85%): `pytest --cov=audiometa --cov-report=term-missing --cov-fail-under=85`
- ✅ New features have corresponding tests
- ✅ Bug fixes include regression tests

**3. Code Cleanup**

- ✅ Remove all debug print statements (`print()`, `pdb`, etc.)
- ✅ Remove all `assert` statements from production code (assert statements are allowed in test code)
- ✅ Remove commented-out code
- ✅ Remove temporary files and test artifacts
- ✅ No hardcoded credentials, API keys, or secrets

**4. Documentation**

- ✅ Update docstrings for new functions/classes (only when needed - see docstring guidelines below)
- ✅ Update README if adding new features or changing behavior
- ✅ Update CONTRIBUTING.md if changing development workflow
- ✅ Add/update type hints where appropriate

**Docstring Guidelines:**

Docstrings should only be added when they provide value (complex logic, public API, edge cases, etc.). When docstrings are needed, use a **systematic Google-style format** for consistency:

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

**When to add docstrings:**

- Public API functions/classes (exported from `__init__.py`)
- Complex business logic that isn't obvious
- Functions with non-obvious side effects
- Important edge cases or assumptions

**When NOT to add docstrings:**

- Simple getter/setter functions
- Self-explanatory functions with descriptive names
- Test functions (unless testing complex scenarios)
- Internal helper functions that are obvious from context

**5. Git Hygiene**

- ✅ Commit messages follow the [commit message convention](#-commit-message-convention)
- ✅ No merge conflicts with target branch
- ✅ Branch is up to date with target branch
- ✅ No accidental commits (large files, secrets, personal configs)

**6. PR Description**

- ✅ Clear description of changes
- ✅ Reference related issues (e.g., "Fixes #123")
- ✅ Note any breaking changes
- ✅ Include testing instructions if applicable

**7. Breaking Changes & Compatibility**

- ✅ Breaking changes are clearly marked in PR description
- ✅ Breaking changes include proper versioning notes (for maintainers to handle)
- ✅ Backward compatibility maintained (unless breaking change is intentional)
- ✅ If breaking change is intentional, clearly document the migration path

#### For Maintainers (Before Merging to `main`)

**All Contributor Checks Plus:**

**1. Code Review**

- ✅ Code follows project conventions and style
- ✅ Logic is sound and well-structured
- ✅ Error handling is appropriate
- ✅ Performance considerations addressed (if applicable)

**2. Testing Verification**

- ✅ CI tests pass on all platforms and Python versions
- ✅ Test coverage is adequate for the changes
- ✅ Edge cases are handled
- ✅ Integration with existing features works correctly

**3. Documentation Review**

- ✅ Public API changes are documented
- ✅ Breaking changes are clearly marked and documented
- ✅ Examples and usage are updated if needed

**4. Compatibility Verification**

- ✅ Breaking changes have proper versioning plan (major version bump)
- ✅ Backward compatibility maintained (unless intentional breaking change)
- ✅ Migration path documented for breaking changes
- ✅ Dependencies are up to date and compatible

**5. Final Checks**

- ✅ PR description is clear and complete
- ✅ All review comments are addressed
- ✅ No unresolved discussions
- ✅ Ready for release (if applicable)

**Quick Pre-PR Command:**

```bash
# Run all checks at once
pre-commit run --all-files && \
pytest --cov=audiometa --cov-report=term-missing --cov-fail-under=85
```

### Releasing _(For Maintainers)_

Releases are created from the `main` branch.

1. Bump your version (increment the version number, e.g., from 1.2.2 to 1.2.3) using bump2version (which automatically finds and updates version references in your project files) or manually editing **version**
2. Update the changelog (`CHANGELOG.md`) with the new release version and changes
   - Contributors should not modify the changelog; this is maintained by maintainers during releases
3. Tag the release (create a Git tag to mark this specific commit as the release point):
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
4. CI/CD will:
   - Run tests
   - Build a package
   - Upload to PyPI (if configured)

## 🪪 License & Attribution

All contributions are made under the project's open-source license.
You retain authorship of your code; the project retains redistribution rights under the same license.

## 🌍 Contact & Discussions

You can open:

- **Issues** → bug reports or new ideas
- **Discussions** → suggestions, architecture, or music-genre topics

Let's make this library grow together 🌱
