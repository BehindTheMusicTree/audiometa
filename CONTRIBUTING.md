# 🧭 Contributing Guidelines

Thank you for your interest in contributing!
This project is currently maintained by a solo developer, but contributions, suggestions, and improvements are welcome.

## Table of Contents

- [🧑‍🤝‍🧑 Contributors vs Maintainers](#-contributors-vs-maintainers)
  - [Roles Overview](#roles-overview)
  - [Infrastructure & Automation Permissions](#infrastructure--automation-permissions)
- [🧱 Development Workflow](#-development-workflow)
  - [0. Fork & Clone](#0-fork--clone)
  - [1. Environment Setup](#1-environment-setup)
  - [2. Branching](#2-branching)
  - [3. Developing](#3-developing)
  - [4. Testing](#4-testing)
  - [5. Committing](#5-committing)
  - [6. Pre-PR Checklist](#6-pre-pr-checklist)
  - [7. Pull Request Process](#7-pull-request-process)
  - [8. Releasing _(For Maintainers)_](#8-releasing-for-maintainers)
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

**Important:** Even maintainers must go through Pull Requests. No direct commits to `main` are allowed - all changes, including those from maintainers, must be submitted via Pull Requests and go through the standard review process.

_Note: Contributors can submit fixes for critical issues via feature branches. Maintainers may promote these to hotfix branches when urgent production fixes are needed._

### Infrastructure & Automation Permissions

**Repository automation policies (maintainer-only):**

- Publishing workflows (`.github/workflows/publish.yml`) - handles sensitive secrets and can publish packages to PyPI
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

## 🧱 Development Workflow

We follow a light GitFlow model adapted for small teams and open-source projects:

**Workflow steps:** Fork & Clone → Environment Setup → Branching → Developing → Testing → Committing → Pre-PR Checklist → Pull Request Process → Releasing _(For Maintainers)_

### 0. Fork & Clone

**For contributors:**

1. Fork the repository on GitHub
2. Clone your fork:

   ```bash
   git clone https://github.com/YOUR-USERNAME/audiometa.git
   cd audiometa
   ```

**For maintainers:**

Clone the main repository directly:

```bash
git clone https://github.com/Andreas-Garcia/audiometa.git
cd audiometa
```

### 1. Environment Setup

Ensure you're using:

- **Python 3.13** (required for development - see note below)

**Note:** While the library itself supports Python 3.12+, the development environment requires Python 3.13 due to:

- The `debug-statements` hook explicitly requires `python3.13`
- Mypy is configured for Python 3.13 in `pyproject.toml`

- Virtual environment with dependencies:

  ```bash
  python -m venv .venv
  source .venv/bin/activate  # (Linux/macOS)
  .venv\Scripts\activate     # (Windows)
  pip install -e ".[dev]"
  ```

- **System dependencies** (required for testing and linting):

  To ensure your local environment matches CI exactly, use the automated installation scripts:

  ```bash
  # Ubuntu/Linux
  ./scripts/install-system-dependencies-ubuntu.sh

  # macOS
  ./scripts/install-system-dependencies-macos.sh

  # Windows
  .\scripts\install-system-dependencies-windows.ps1
  ```

  These scripts install the same versions as CI. Configuration is documented in `system-dependencies-prod.toml`, `system-dependencies-test-only.toml`, and `system-dependencies-lint.toml`.

  **Required tools:**
  - `ffmpeg` / `ffprobe` - Audio file analysis
  - `flac` / `metaflac` - FLAC file operations
  - `mediainfo` - Media information extraction
  - `id3v2` - ID3v2 tag manipulation
  - `bwfmetaedit` - BWF metadata editing (for WAV files)
  - `mid3v2` - Provided by mutagen (Python package)

### 2. Branching

#### Main Branch (`main`)

- The stable, always-deployable branch
- All tests must pass before merging
- Releases are tagged from `main`
- **No direct commits allowed** - All changes must go through Pull Requests, including changes from maintainers

#### Feature Branches (`feature/<name>`)

- Create one for each new feature or bug fix
- Example:
  ```bash
  git checkout -b feature/improve-genre-classification
  ```
- Merge into `main` via Pull Request when complete and tested

#### Hotfix Branches (`hotfix/<issue>`) _(For Maintainers)_

- For urgent bug fixes on production versions
- Contributors can submit fixes via feature branches that maintainers may promote to hotfixes if needed

#### Chore Branches (`chore/<name>`)

- For maintenance, infrastructure, and configuration work
- Examples: repository setup, CI/CD changes, dependency updates, documentation infrastructure
- Valid in lightweight GitFlow/GitHub Flow workflows
- Example:
  ```bash
  git checkout -b chore/github-setup
  git checkout -b chore/update-dependencies
  ```
- Merge into `main` via Pull Request when complete

### 3. Developing

See [DEVELOPMENT.md](DEVELOPMENT.md) for coding standards and best practices, including code style conventions, type checking rules, and known linting issues.

### 4. Testing

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

**Note:** CI tests run on pinned OS versions (e.g., Ubuntu 22.04, macOS 14) for consistency. OS versions are pinned in `.github/workflows/ci.yml` to ensure system package version availability and consistency with pinned versions in `system-dependencies-prod.toml`, `system-dependencies-test-only.toml`, and `system-dependencies-lint.toml`. Python package versions are pinned in `pyproject.toml`. This prevents breakages when GitHub Actions updates `-latest` runners. See `.github/workflows/ci.yml` for the specific pinned OS versions.

**System dependency version verification:** Before running any tests, pytest automatically verifies that installed system dependency versions (ffmpeg, flac, mediainfo, id3v2, bwfmetaedit, exiftool) match the pinned versions defined in `system-dependencies-prod.toml` and `system-dependencies-test-only.toml`. This uses the shared `scripts/verify-system-dependency-versions.py` script (also used by pre-commit hooks and installation scripts). If versions don't match, pytest will exit with an error message before running tests. This ensures tests always run with the exact same tool versions as CI and local development environments. To fix version mismatches, update your system dependencies using the installation scripts: `./scripts/install-system-dependencies-ubuntu.sh` (Ubuntu), `./scripts/install-system-dependencies-macos.sh` (macOS), or `.\scripts\install-system-dependencies-windows.ps1` (Windows).

**Note:** On Windows, version verification skips optional tools (`id3v2`, `mediainfo`, `exiftool`) that are not needed for e2e tests. See the Windows CI differences section below for details.

**Windows WSL requirement:** On Windows, the `id3v2` tool is not available as a native Windows binary. The installation script attempts to use **WSL (Windows Subsystem for Linux)** to install `id3v2` via Ubuntu's package manager, but WSL installation complexity (requiring system restarts, DISM configuration, and Ubuntu distribution setup) has prevented successful full installation in practice. This is why Windows CI only runs e2e tests (which don't require `id3v2`). For local development, the script will attempt WSL installation, but manual WSL setup may be required. A wrapper script (`id3v2.bat`) is created if WSL installation succeeds to make `id3v2` accessible from Windows command line.

**Windows CI differences:** Windows CI only runs e2e tests (unit and integration tests run on Ubuntu and macOS). This is due to WSL installation complexity preventing full dependency installation. As a result, some dependencies are skipped in Windows CI:

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

### 5. Committing

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

### 6. Pre-PR Checklist

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

### 7. Pull Request Process

When you open a Pull Request, several automations will run automatically:

- **Auto-labeling**: Component labels (like `id3v1`, `id3v2`, `vorbis`, `riff`, `cli`, `core`) and some type labels (`documentation`, `test`, `ci`, `dependencies`) are automatically added based on files changed
- **Manual labels**: You should still add type labels (`bug`, `enhancement`, `feature`) and priority labels manually, as these can't be determined from file paths
- **Auto-assignment**: For contributor PRs (not maintainer PRs), reviewers are automatically assigned
- **CI/CD checks**: Automated tests, linting, and type checking run on your PR
- **Welcome message**: First-time contributors receive a welcome message with helpful links

These automations help streamline the review process and ensure consistency across the project.

### 8. Releasing _(For Maintainers)_

Releases are created from the `main` branch.

**For detailed PyPI publishing instructions, see [PyPI Publishing Guide](docs/PYPI_PUBLISHING.md).**

Quick release process:

1. **Ensure you're on the `main` branch** - Releases must be prepared from `main`, not from feature branches

   ```bash
   git checkout main
   git pull origin main
   ```

2. Check `TODO.md` for any critical items that should be addressed before release
   - Review high-priority tasks and ensure they're either completed or deferred to next release
   - Update TODO items if needed to reflect current project status

3. Update the changelog (`CHANGELOG.md`) with the new release version and changes
   - Review changes since last release and decide on version number (following Semantic Versioning)
   - Move content from `[Unreleased]` section to new version entry with date (e.g., `## [0.2.3] - 2025-11-17`)
   - Contributors should not modify the changelog; this is maintained by maintainers during releases

4. Bump version numbers using `bump2version`:

   ```bash
   # Activate virtual environment (required for pre-commit hooks)
   source .venv/bin/activate

   # Use bump2version to update version numbers in all configured files
   # This will update pyproject.toml and README.md automatically
   bump2version --new-version 0.2.3 patch

   # Or use semantic versioning parts:
   # bump2version patch    # 0.2.2 -> 0.2.3
   # bump2version minor    # 0.2.2 -> 0.3.0
   # bump2version major    # 0.2.2 -> 1.0.0
   ```

   **What bump2version does:**
   - Updates version in `pyproject.toml` (from `.bumpversion.cfg` configuration)
   - Updates version badge in `README.md`
   - Creates a commit with the configured commit message (e.g., "chore: prepare release 0.2.3")
   - Does NOT update `CHANGELOG.md` (this is done manually in step 2)

   **Configuration:** The `.bumpversion.cfg` file specifies which files to update. See the file for details.

5. Verify changes and push:

   ```bash
   # Review the commit created by bump2version
   git log -1

   # Push the release commit
   git push origin main
   ```

6. Tag the release (create a Git tag to mark this specific commit as the release point):

   ```bash
   git tag v0.2.3
   git push origin v0.2.3
   ```

   **Important:** The tag version must match the version in `pyproject.toml` (without the `v` prefix).

7. CI/CD will automatically:
   - **Wait for CI to complete**: The publish workflow automatically waits for CI to finish (polls every 30 seconds, max 30 minutes)
   - Verify tag version matches `pyproject.toml` version
   - Verify tag is on main branch
   - Verify CI has passed for the tagged commit
   - Build the package (source distribution and wheel)
   - Publish to TestPyPI (for testing)
   - Verify TestPyPI installation works correctly
   - Publish to PyPI using the `PYPI_API_TOKEN` secret
   - Verify PyPI publication success

   **Note:** The publish workflow will automatically wait for CI to complete, so you don't need to manually re-run it if CI is still running when you push the tag.

**Note:** Ensure `PYPI_API_TOKEN` is configured in GitHub repository secrets before tagging. See [PyPI Publishing Guide](docs/PYPI_PUBLISHING.md) for setup instructions.

**Alternative:** If you prefer to update versions manually instead of using `bump2version`, you can manually edit `pyproject.toml` and `README.md`, then commit the changes yourself.

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
