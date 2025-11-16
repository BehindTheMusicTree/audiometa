# 🧭 Contributing Guidelines

Thank you for your interest in contributing!
This project is currently maintained by a solo developer, but contributions, suggestions, and improvements are welcome.

## Table of Contents

- [🧑‍🤝‍🧑 Contributors vs Maintainers](#-contributors-vs-maintainers)
  - [Roles Overview](#roles-overview)
  - [Infrastructure & Automation Permissions](#infrastructure--automation-permissions)
- [💻 Contributing Code](#-contributing-code)
- [📦 Environment Setup](#-environment-setup)
- [🧱 Development Workflow](#-development-workflow)
  - [Main Branch (`main`)](#main-branch-main)
  - [Feature Branches (`feature/<name>`)](#feature-branches-featurename)
  - [Hotfix Branches (`hotfix/<issue>`)](#hotfix-branches-hotfixissue)
  - [Chore Branches (`chore/<name>`)](#chore-branches-chorename)
  - [🧪 Testing](#-testing)
    - [Run Local Tests](#run-local-tests)
    - [Run Coverage](#run-coverage)
      - [Running Tests with Coverage](#running-tests-with-coverage)
      - [Running Tests Without Coverage](#running-tests-without-coverage)
      - [Viewing Coverage Reports](#viewing-coverage-reports)
    - [Lint Code for Style Consistency](#lint-code-for-style-consistency)
      - [Setup and Usage](#setup-and-usage)
      - [Pre-commit Hooks](#pre-commit-hooks)
      - [Auto-fix Formatting](#auto-fix-formatting)
      - [Type Checking](#type-checking)
      - [Code Style Conventions](#code-style-conventions)
      - [Known Linting Issues](#known-linting-issues)
  - [📝 Commit Message Convention](#-commit-message-convention)
  - [✅ Pre-PR / Pre-Merge Checklist](#-pre-pr--pre-merge-checklist)
  - [🚀 Releasing _(For Maintainers)_](#releasing-for-maintainers)
- [🪪 License & Attribution](#-license--attribution)
- [🌍 Contact & Discussions](#-contact--discussions)

## Contributors vs Maintainers

### Roles Overview

**Contributors**

Anyone can be a contributor by:

- Submitting bug reports or feature requests via GitHub Issues (use the issue templates for bug reports and feature requests)
- Proposing code changes through Pull Requests (the PR template will guide you through the process)
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
- Managing the TODO list (contributors should open issues for new tasks; maintainers update `TODO.md`)
- Managing repository automation (stale issues/PRs, auto-labeling, auto-assignment, etc.)

_Note: Contributors can submit fixes for critical issues via feature branches. Maintainers may promote these to hotfix branches when urgent production fixes are needed._

### Infrastructure & Automation Permissions

**Repository automation policies (maintainer-only):**

- Stale issues/PRs workflow (`.github/workflows/stale.yml`) - affects repository management policies
- Auto-assignment workflows - affects review process
- Other automation workflows that affect repository management

**Auto-labeling configuration (contributors can suggest changes via PRs):**

- Auto-labeling configuration (`.github/labeler.yml`) - contributors can suggest updates when adding new features/components
- Example: If adding a new audio format handler, contributor can suggest adding label rules for that component
- Maintainers review and approve label configuration changes

**Why most automation is maintainer-only:**

- These workflows implement repository policies and management decisions
- Changes can affect how issues/PRs are handled, categorized, and maintained
- They require understanding of project management strategy

**What contributors can do:**

- Suggest changes to auto-labeling configuration (`.github/labeler.yml`) via PRs, especially when adding new features/components
- Suggest improvements or report issues with automation via GitHub Issues
- Add/remove labels on their own issues and PRs (type labels like `bug`, `enhancement`, priority labels, etc.)
- Discuss automation behavior in discussions or issues

**What contributors cannot do:**

- Modify automation workflows (stale, auto-assignment, etc.) - these are policy decisions
- Create or delete repository labels (maintainer-only) - repository labels are the label definitions (like `bug`, `enhancement`, `id3v1`) that exist in the repository's label list
- Modify labels on issues/PRs they didn't create (unless they have write access)

Currently, this project has a solo maintainer, but the role may expand as the project grows.

## 💡 Contributing Code

1. Fork the repository
2. Create a `feature/` branch
3. Run tests locally
4. Open a Pull Request with a clear description
   - GitHub will automatically use the PR template to guide you through the process
   - Fill out all relevant sections in the template

## 📦 Environment Setup

Ensure you're using:

- Python 3.12 or 3.13

- Virtual environment with dependencies:

  ```bash
  python -m venv .venv
  source .venv/bin/activate  # (Linux/macOS)
  .venv\Scripts\activate     # (Windows)
  pip install -e ".[dev]"
  ```

- **System dependencies** (required for testing):

  To ensure your local environment matches CI exactly, use the automated setup script:

  ```bash
  # Linux/macOS
  ./scripts/setup-system-dependencies.sh

  # Windows
  .\scripts\install-system-dependencies-windows.ps1
  ```

  This installs the same versions as CI. Configuration is documented in `system-dependencies.toml`.

  **Required tools:**
  - `ffmpeg` / `ffprobe` - Audio file analysis
  - `flac` / `metaflac` - FLAC file operations
  - `mediainfo` - Media information extraction
  - `id3v2` - ID3v2 tag manipulation
  - `bwfmetaedit` - BWF metadata editing (for WAV files)
  - `mid3v2` - Provided by mutagen (Python package)

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

### Chore Branches (`chore/<name>`)

- For maintenance, infrastructure, and configuration work
- Examples: repository setup, CI/CD changes, dependency updates, documentation infrastructure
- Valid in lightweight GitFlow/GitHub Flow workflows
- Example:
  ```bash
  git checkout -b chore/github-setup
  git checkout -b chore/update-dependencies
  ```
- Merge into `main` via Pull Request when complete

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

**Note:** CI tests run on pinned OS versions for consistency. OS versions are pinned to ensure package version availability and consistency with pinned package versions. This prevents breakages when GitHub Actions updates `-latest` runners. See `.github/workflows/ci.yml` for the specific pinned versions.

**System dependency version verification:** Before running any tests, pytest automatically verifies that installed system dependency versions (ffmpeg, flac, mediainfo, id3v2, bwfmetaedit, exiftool) match the pinned versions defined in `system-dependencies.toml`. If versions don't match, pytest will exit with an error message before running tests. This ensures tests always run with the exact same tool versions as CI and local development environments. To fix version mismatches, update your system dependencies using the setup script: `./scripts/setup-system-dependencies.sh` (Linux/macOS) or `.\scripts\install-system-dependencies-windows.ps1` (Windows).

**Note:** On Windows, version verification skips optional tools (`id3v2`, `mediainfo`, `exiftool`) that are not needed for e2e tests. See the Windows CI differences section below for details.

**Windows WSL requirement:** On Windows, the `id3v2` tool is not available as a native Windows binary. The installation script automatically installs **WSL (Windows Subsystem for Linux)** and uses it to install `id3v2` via Ubuntu's package manager. This ensures version pinning consistency with Ubuntu CI. A wrapper script (`id3v2.bat`) is created to make `id3v2` accessible from Windows command line. If WSL installation requires a restart, the script will prompt you to restart and run it again.

**Windows CI differences:** Windows CI only runs e2e tests (unit and integration tests run on Ubuntu and macOS). As a result, some dependencies are skipped in Windows CI to reduce installation complexity:

- **Skipped in Windows CI:**
  - `mediainfo` - Only used in integration tests for verification, not needed for e2e tests
  - `exiftool` - Not used in e2e tests
  - `id3v2` - Optional (only needed for FLAC files with ID3v2 tags, which e2e tests don't use)

- **Required in Windows CI:**
  - `ffmpeg` / `ffprobe` - Needed for `get_bitrate()` and `get_duration_in_sec()` on WAV files
  - `flac` / `metaflac` - Needed for FLAC metadata writing via Vorbis
  - `bwfmetaedit` - Needed for WAV metadata writing via RIFF

The installation script automatically detects CI environment and skips unnecessary dependencies. Version verification in pytest also skips these optional tools on Windows.

For detailed test documentation, including test principles, markers, and advanced usage, see [`audiometa/test/README.md`](audiometa/test/README.md).

#### Lint Code for Style Consistency

We use [pre-commit](https://pre-commit.com/) hooks to automatically check code quality before commits.

##### Setup and Usage

**First-time setup:**

```bash
# Recommended: Use the setup script (ensures proper environment)
./scripts/setup-precommit.sh

# Or manually:
# 1. Activate your virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 2. Install dev dependencies (this installs the exact tool versions from pyproject.toml)
pip install -e ".[dev]"

# 3. Install pre-commit hooks
pre-commit install
```

**Important:** All Python tools use `language: system`, which means they run from your active Python environment. **Always activate your virtual environment before committing** to ensure the hooks use the correct tool versions defined in `pyproject.toml` (matching CI).

**Version enforcement:** A validation hook automatically checks that your installed tool versions (ruff, isort, mypy, docformatter) match those in `pyproject.toml`. If there's a mismatch, pre-commit will fail with clear instructions to fix it. This ensures consistency between local development, pre-commit hooks, and CI.

**Exception:** prettier (for Markdown formatting) is a Node.js tool and uses an external repository with a pinned version - it's the only tool not managed through `pyproject.toml`.

Once installed, pre-commit will automatically run on every commit. You can also run it manually:

```bash
# Run on all files
pre-commit run --all-files

# Run only on staged files (default when committing)
pre-commit run
```

##### Pre-commit Hooks

The following hooks run in execution order:

1. **check-tool-versions**: Validates that installed tool versions (ruff, isort, mypy) match `pyproject.toml`
   - Manual: `pre-commit run check-tool-versions`
   - **Runs first** to fail fast if versions don't match (before any other checks)
   - Ensures consistency between local development, pre-commit hooks, and CI
   - Also verifies that a virtual environment is active

2. **check-yaml**: Validates YAML file syntax
   - Manual: `pre-commit run check-yaml --all-files`

3. **check-added-large-files**: Prevents committing files larger than 10MB
   - Manual: `pre-commit run check-added-large-files --all-files`

4. **check-json**: Validates JSON file syntax
   - Manual: `pre-commit run check-json --all-files`

5. **check-toml**: Validates TOML file syntax
   - Manual: `pre-commit run check-toml --all-files`

6. **verify-system-dependency-versions**: Verifies installed system dependency versions match pinned versions in `system-dependencies.toml`
   - Manual: `pre-commit run verify-system-dependency-versions --all-files`
   - Validates that `system-dependencies.toml` can be parsed
   - Checks that installed tool versions match pinned versions
   - Prevents committing when dependencies are misconfigured
   - Runs on every commit to catch version mismatches early

7. **check-merge-conflict**: Detects merge conflict markers
   - Manual: `pre-commit run check-merge-conflict --all-files`

8. **debug-statements**: Detects debug statements (pdb, ipdb, etc.)
   - Manual: `pre-commit run debug-statements --all-files`

9. **trailing-whitespace**: Automatically removes trailing whitespace from all files
   - Manual: `pre-commit run trailing-whitespace --all-files`
   - Note: Like all file-modifying hooks, commits will fail if this hook makes changes (see "How File-Modifying Hooks Work" section below)
   - Note: For Python files, `ruff-format` also removes trailing whitespace, making this hook redundant for Python files. However, it's kept because it handles non-Python files (markdown, YAML, etc.) that `ruff-format` cannot process.

10. **no-assert**: Custom hook that prevents `assert` statements in production code (use proper exceptions instead)

- Manual: `pre-commit run no-assert --all-files`

11. **isort**: Sorts and organizes import statements according to PEP 8

- Manual: `isort .`

12. **ruff-format**: Formats Python code (replaces black) - handles code formatting and EOF newlines automatically
    - Manual: `ruff format .`

13. **ruff**: Auto-fixes linting issues (unused imports/variables, code style, line length, etc.) - replaces autoflake and flake8
    - Manual: `ruff check --fix .`

14. **docformatter**: Formats docstrings (triple-quoted strings) according to PEP 257
    - Manual: `docformatter --in-place --wrap-summaries=120 --wrap-descriptions=120 .`

15. **fix-long-comments**: Custom hook that automatically wraps long comment lines (starting with `#`) to fit within 120 characters
    - Manual: `pre-commit run fix-long-comments --all-files`

16. **mypy**: Static type checking - reports type errors but does not auto-fix
    - Manual: `mypy audiometa`

17. **prettier**: Formats Markdown files (`.md`, `.markdown`) - ensures consistent formatting, preserves list numbering
    - Manual: `prettier --write "**/*.md"`

18. **py-psscriptanalyzer**: Lints PowerShell scripts (`.ps1` files) - checks for code quality issues, style violations, and potential bugs
    - Manual: `pre-commit run py-psscriptanalyzer --all-files`
    - Checks Error and Warning severity levels
    - Ensures PowerShell scripts follow best practices

19. **py-psscriptanalyzer-format**: Formats PowerShell scripts (`.ps1` files) - applies consistent formatting
    - Manual: `pre-commit run py-psscriptanalyzer-format --all-files`
    - Automatically formats PowerShell code to ensure consistency

##### How File-Modifying Hooks Work

**Important**: All hooks that modify files (formatting, sorting, fixing) will cause your commit to fail if they make changes. This is intentional and is a safety feature built into pre-commit.

**Hooks that modify files:**

- `trailing-whitespace` - Removes trailing whitespace
- `isort` - Sorts imports
- `ruff-format` - Formats code
- `ruff` (with `--fix`) - Auto-fixes linting issues
- `docformatter` - Formats docstrings
- `fix-long-comments` - Wraps long comment lines
- `py-psscriptanalyzer-format` - Formats PowerShell scripts

**Why commits fail:**
When a hook modifies a file, it updates the file in your working directory but not in the staging area. Git detects this mismatch (staged version ≠ working directory version) and refuses to commit to prevent committing code that doesn't match what's on disk.

**The workflow:**

```bash
git add file.py
git commit -m "message"  # Hook modifies file → commit fails
git add file.py          # Re-stage the fixed file
git commit -m "message"  # Now succeeds ✓
```

**Why this design:**

- Forces you to review what the hook changed
- Prevents accidental commits of unexpected modifications
- Ensures you explicitly approve the changes before committing
- Maintains consistency between staged and working directory

**Note**: This applies to ALL file-modifying hooks, including built-in hooks, third-party hooks, and custom hooks. There are no exceptions - this is a universal pre-commit safety feature.

##### Type Checking

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
  - Missing type stubs for external libraries are handled via mypy overrides in `pyproject.toml` (e.g., `mutagen.*`, `pytest`)
  - **Note**: Do not add `# type: ignore[import-not-found]` comments for libraries that already have mypy overrides configured, as mypy will report them as unused

- **Test code** (`audiometa/test/`): Relaxed type checking
  - Functions can be untyped (no type annotations required)
  - Missing type annotations for variables are allowed
  - This allows test code to be more flexible while maintaining type safety in production code
  - **Note on pytest type stubs**: Mypy will report "Cannot find implementation or library stub for module named 'pytest'" because pytest type stubs are not available as a separate package. This is expected and acceptable - real import errors are still caught by test execution at runtime. The mypy overrides in `pyproject.toml` relax type checking rules for test files to accommodate this.

This means:

- You can commit individual files even if other files have type errors
- Before opening a PR, run `pre-commit run --all-files` or `mypy audiometa` to check the entire codebase
- CI will catch any type errors in the full codebase before merging
- Test code type errors are acceptable as long as they don't prevent tests from running

CI will automatically test all pushes and PRs using GitHub Actions.

##### Code Style Conventions

**Module Naming:**

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

##### Known Linting Issues

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

### ✅ Pre-PR / Pre-Merge Checklist

Before submitting a Pull Request (contributors) or merging to `main` (maintainers), ensure the following checks are completed:

#### For Contributors (Before Opening a PR)

**1. Code Quality**

- ✅ Remove commented-out code
- ✅ No hardcoded credentials, API keys, or secrets
- ✅ Run pre-commit hooks: `pre-commit run --all-files` (includes linting, formatting, type checking, assert statement check, debug statement detection, etc.)

**2. Tests**

- ✅ All tests pass: `pytest`
- ✅ Coverage meets threshold (≥85%): `pytest --cov=audiometa --cov-report=term-missing --cov-fail-under=85`
- ✅ New features have corresponding tests
- ✅ Bug fixes include regression tests

**3. Documentation**

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

**4. Git Hygiene**

- ✅ Commit messages follow the [commit message convention](#-commit-message-convention)
- ✅ No merge conflicts with target branch
- ✅ Branch is up to date with target branch
- ✅ No accidental commits (large files, secrets, personal configs)

**5. PR Description**

- ✅ Clear description of changes
- ✅ Reference related issues (e.g., "Fixes #123")
- ✅ Note any breaking changes
- ✅ Include testing instructions if applicable

**6. Breaking Changes**

- ✅ If this PR includes breaking changes, they are clearly documented
- ✅ Migration path is provided (if applicable)
- ✅ Breaking changes include proper versioning notes (for maintainers to handle)

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

### What Happens When You Submit a PR

When you open a Pull Request, several automations will run automatically:

- **Auto-labeling**: Component labels (like `id3v1`, `id3v2`, `vorbis`, `riff`, `cli`, `core`) and some type labels (`documentation`, `test`, `ci`, `dependencies`) are automatically added based on files changed
- **Manual labels**: You should still add type labels (`bug`, `enhancement`, `feature`) and priority labels manually, as these can't be determined from file paths
- **Auto-assignment**: For contributor PRs (not maintainer PRs), reviewers are automatically assigned
- **CI/CD checks**: Automated tests, linting, and type checking run on your PR
- **Welcome message**: First-time contributors receive a welcome message with helpful links

These automations help streamline the review process and ensure consistency across the project.

### Releasing _(For Maintainers)_

Releases are created from the `main` branch.

**For detailed PyPI publishing instructions, see [PyPI Publishing Guide](docs/PYPI_PUBLISHING.md).**

Quick release process:

1. Check `TODO.md` for any critical items that should be addressed before release
   - Review high-priority tasks and ensure they're either completed or deferred to next release
   - Update TODO items if needed to reflect current project status
2. Update the changelog (`CHANGELOG.md`) with the new release version and changes
   - Review changes since last release and decide on version number (following Semantic Versioning)
   - Move content from `[Unreleased]` section to new version entry with date
   - Contributors should not modify the changelog; this is maintained by maintainers during releases
3. Bump your version (increment the version number to match the changelog, e.g., from 1.2.2 to 1.2.3) using bump2version (which automatically finds and updates version references in your project files) or manually editing **version** in `pyproject.toml`
4. Commit changes:
   ```bash
   git add pyproject.toml CHANGELOG.md TODO.md
   git commit -m "chore: prepare release 1.2.3"
   git push origin main
   ```
5. Tag the release (create a Git tag to mark this specific commit as the release point):
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
6. CI/CD will automatically:
   - Verify tag version matches `pyproject.toml` version
   - Build the package (source distribution and wheel)
   - Publish to PyPI using the `PYPI_API_TOKEN` secret
   - Verify publication success

**Note:** Ensure `PYPI_API_TOKEN` is configured in GitHub repository secrets before tagging. See [PyPI Publishing Guide](docs/PYPI_PUBLISHING.md) for setup instructions.

## 🪪 License & Attribution

All contributions are made under the project's open-source license.
You retain authorship of your code; the project retains redistribution rights under the same license.

## 📜 Code of Conduct

This project adheres to a Code of Conduct to ensure a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) when participating in this project.

## 🌍 Contact & Discussions

You can open:

- **Issues** → bug reports or new ideas
- **Discussions** → suggestions, architecture, or music-genre topics

For more detailed support information, see [SUPPORT.md](SUPPORT.md).

Let's make this library grow together 🌱
