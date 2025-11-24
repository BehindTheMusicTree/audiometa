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
  - [6. Pull Request Process](#6-pull-request-process)
    - [6.1. Pre-PR Checklist](#61-pre-pr-checklist)
    - [6.2. Opening a Pull Request](#62-opening-a-pull-request)
  - [7. Releasing _(For Maintainers)_](#7-releasing-for-maintainers)
- [🪪 License & Attribution](#-license--attribution)
- [📜 Code of Conduct](#-code-of-conduct)
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
- Moving "Unreleased" changelog entries to versioned sections during releases
- Managing the TODO list (contributors should open issues for new tasks; maintainers update `TODO.md`)
- Managing repository automation (stale issues/PRs, auto-labeling, auto-assignment, etc.)

**Important:** Even maintainers must go through Pull Requests. No direct commits to `main` are allowed - all changes, including those from maintainers, must be submitted via Pull Requests and go through the standard review process.

_Note: Contributors can submit fixes for critical issues via feature branches. Maintainers may promote these to hotfix branches when urgent production fixes are needed._

### Infrastructure & Automation Permissions

**Repository automation policies (maintainer-only):**

- Publishing workflows (`.github/workflows/publish.yml`) - handles sensitive secrets and can publish packages to PyPI
- Stale issues/PRs workflow (`.github/workflows/stale.yml`) - affects repository management policies
- Auto-assignment workflows (`.github/workflows/auto-assign.yml`) - affects review process
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

**Workflow steps:** Fork & Clone → Environment Setup → Branching → Developing → Testing → Committing → Pull Request Process (including Pre-PR Checklist) → Releasing _(For Maintainers)_

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

- **Python 3.12, 3.13, or 3.14** (all supported - see note below)

**Note:** While the library itself supports Python 3.12+, the development environment works with Python 3.12, 3.13, or 3.14:

- Pre-commit hooks use Python from your activated virtual environment (`language: system`)
- Mypy 1.18.2 runs on Python 3.12, 3.13, or 3.14 and is configured to type-check against Python 3.12 syntax (ensures code is compatible with the minimum supported version)
  - **Why Python 3.12 for mypy?** Setting `python_version = "3.12"` in `pyproject.toml` ensures type-checking validates code against the minimum supported Python version. This prevents accidentally using Python 3.13/3.14-only type features that would break compatibility with Python 3.12. While Python 3.14 is backward compatible and doesn't introduce breaking type system changes, this configuration ensures the codebase remains compatible with all supported versions. If Python 3.14-specific type features are needed in the future, `python_version` can be updated accordingly.
- Ruff is configured with `target-version = "py312"` for the same compatibility reasons
- All hooks work with Python 3.12, 3.13, or 3.14
- **Python 3.14**: Fully supported. No special installation steps are needed.

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
- Include issue numbers when applicable: `feature/123-add-ogg-support`
- Examples:
  ```bash
  git checkout -b feature/improve-genre-classification
  git checkout -b feature/123-add-ogg-support        # With issue number
  git checkout -b feature/456-fix-id3v1-encoding      # With issue number
  ```
- Merge into `main` via Pull Request when complete and tested

#### Hotfix Branches (`hotfix/<name>`) _(For Maintainers)_

- For urgent bug fixes on production versions
- Include issue numbers when applicable: `hotfix/789-critical-bug`
- Examples:
  ```bash
  git checkout -b hotfix/critical-metadata-bug
  git checkout -b hotfix/789-critical-security-patch   # With issue number
  ```
- Contributors can submit fixes via feature branches that maintainers may promote to hotfixes if needed

#### Chore Branches (`chore/<name>`)

- For maintenance, infrastructure, and configuration work
- Include issue numbers when applicable: `chore/234-update-dependencies`
- Examples: repository setup, CI/CD changes, dependency updates, documentation infrastructure
- Valid in lightweight GitFlow/GitHub Flow workflows
- Examples:
  ```bash
  git checkout -b chore/github-setup
  git checkout -b chore/update-dependencies
  git checkout -b chore/234-update-dependencies        # With issue number
  ```
- Merge into `main` via Pull Request when complete

#### Working with Multiple Local Branches (Git Worktrees)

When working on multiple branches simultaneously or when you need separate Cursor windows for different branches, use **git worktrees**. This allows you to have multiple working directories for the same repository, each on a different branch.

For detailed information on setting up and using git worktrees, see:

**[Git Worktrees Guide](docs/GIT_WORKTREES.md)**

### 3. Developing

See [DEVELOPMENT.md](DEVELOPMENT.md) for coding standards and best practices, including code style conventions, type checking rules, and known linting issues.

### 4. Testing

We use pytest for all automated testing with markers for unit, integration, and e2e tests.

#### Quick Reference

```bash
# Run all tests
pytest

# Run tests by category
pytest -m unit          # Fast unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e           # End-to-end tests only

# Run without slow e2e tests
pytest -m "not e2e"

# Run with coverage (recommended before committing)
pytest --cov=audiometa --cov-report=html --cov-report=term-missing --cov-fail-under=85
```

**For comprehensive test documentation**, including test principles, markers, coverage details, Windows testing, CI configuration, and advanced usage, see [`docs/TESTING.md`](docs/TESTING.md).

### 5. Committing

We follow a structured commit format inspired by [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

**IMPORTANT:** Always activate the project's virtual environment (`.venv`) before committing. Pre-commit hooks require the correct Python environment.

**Quick reference:**

- Format: `<type>(<scope>): <summary>`
- Run pre-commit hooks: `pre-commit run --all-files`
- Activate virtual environment: `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)

**For comprehensive commit message guidelines**, including format details, commit types, scopes, examples, and pre-commit hook information, see [`docs/COMMITTING.md`](docs/COMMITTING.md).

### 6. Pull Request Process

#### 6.1. Pre-PR Checklist

Before submitting a Pull Request, ensure the following checks are completed:

**1. Code Quality**

- ✅ Follow [Code Quality](DEVELOPMENT.md#code-quality) standards in DEVELOPMENT.md
- ✅ Run pre-commit hooks: `pre-commit run --all-files` (includes linting, formatting, type checking, assert statement check, debug statement detection, etc.)

**2. Tests**

- ✅ All tests pass: `pytest`
- ✅ Coverage meets threshold (≥85%): `pytest --cov=audiometa --cov-report=term-missing --cov-fail-under=85`
- ✅ New features have corresponding tests
- ✅ Bug fixes include regression tests

**3. Documentation**

- ✅ Update docstrings for new functions/classes (only when needed - see [Docstrings](DEVELOPMENT.md#docstrings) section in DEVELOPMENT.md)
- ✅ Update README or other more focused documentation if adding new features or changing behavior
- ✅ Add/update type hints where appropriate
- ✅ Update `CHANGELOG.md` with your changes in the `[Unreleased]` section (see [Changelog Best Practices](CHANGELOG.md#changelog-best-practices) for guidelines)
- ⚠️ Update CONTRIBUTING.md only in exceptional cases (e.g., when adding hooks for new features in other languages)

**4. Git Hygiene**

- ✅ Commit messages follow the [commit message convention](docs/COMMITTING.md)
- ✅ Branch is up to date with target branch (merge conflicts can be resolved through the PR interface or locally)
- ✅ No accidental commits (large files, secrets, personal configs)

#### For Maintainers (Before Opening/Merging a PR)

**All Contributor Checks Plus:**

**1. Code Review**

- ✅ Code follows project conventions and style
- ✅ Logic is sound and well-structured
- ✅ Error handling is appropriate
- ✅ Performance considerations addressed (if applicable)

**2. Testing Verification**

- ✅ CI tests pass on all platforms and Python versions (CI automatically blocks merge if tests fail)
- ✅ Test coverage meets threshold (CI automatically blocks merge if coverage is below 85%)
- ✅ Edge cases are handled
- ✅ Integration with existing features works correctly

**3. Documentation Review**

- ✅ Public API changes are documented
- ✅ Breaking changes are clearly marked and documented
- ✅ Examples and usage are updated if needed
- ✅ Update CONTRIBUTING.md if changing development workflow (contributors may update CONTRIBUTING.md in exceptional cases, e.g., when adding hooks for new features in other languages)

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

#### 6.2. Opening a Pull Request

**Before opening a Pull Request, ensure you have completed the [Pre-PR Checklist](#61-pre-pr-checklist) above.**

##### PR Title Naming Convention

Pull Request titles must follow the same format as commit messages for consistency:

**Format:**

```
<type>(<optional-scope>): <short imperative description>
```

**Allowed Types:**

- `feat` — new feature
- `fix` — bug fix
- `refactor` — code restructuring
- `docs` — documentation update
- `chore` — maintenance / infrastructure (dependency updates, tooling setup, repository configuration)
- `perf` — performance improvement
- `style` — formatting / lint-only changes
- `ci` — CI/CD pipeline changes (GitHub Actions workflows, CI configuration)

**Rules:**

- Use imperative mood ("Add…", "Fix…", "Update…")
- Keep it under ~70 characters
- Include issue/ticket IDs when applicable (e.g., `fix(#482): handle null values`)
- Avoid "WIP" in titles — use draft PRs instead
- Use lowercase for type and scope (e.g., `feat(id3v2):`, not `Feat(ID3v2):`)

**Note on Branch Prefixes vs PR Title Types:**

Branch prefixes (`feature/`, `chore/`, `hotfix/`) are for branch organization and differ from PR title types:

- Branch `feature/add-flac-support` → PR title: `feat: add flac support` (use `feat`, not `feature`)
- Branch `chore/update-dependencies` → PR title: `chore: update dependencies` (use `chore`)
- Branch `hotfix/critical-bug` → PR title: `fix: critical bug` (use `fix`, not `hotfix`)

**Note on GitHub's Auto-Suggested Titles:**

GitHub automatically generates PR titles based on branch names. For example, a branch named `chore/auto-approve-maintainer-prs` will generate:

```
Chore/auto approve maintainer prs
```

**GitHub's auto-suggested titles do not follow our convention**, so you must rewrite them to match the standard format:

- ❌ **GitHub suggestion**: `Feature/add album artist tag support id3v2` (from branch `feature/add-album-artist-tag-support-id3v2`)
- ✅ **Correct format**: `feat(id3v2): add album artist tag support`

- ❌ **GitHub suggestion**: `Feature/123 add ogg support` (from branch `feature/123-add-ogg-support`)
- ✅ **Correct format**: `feat(ogg): add OGG support`

- ❌ **GitHub suggestion**: `Chore/format code with ruff` (from branch `chore/format-code-with-ruff`)
- ✅ **Correct format**: `style: format code with ruff`

- ❌ **GitHub suggestion**: `Chore/use PAT for auto approve workflow instead of GITHUB_TOKEN` (from branch `chore/use-pat-for-auto-approve-workflow`)
- ✅ **Correct format**: `ci: use PAT for auto-approve workflow instead of GITHUB_TOKEN`

**Examples:**

- `feat(id3v2): add album artist tag support`
- `fix(vorbis): correctly parse embedded picture metadata`
- `docs: update contributing guide`
- `chore: auto-approve maintainer PRs`
- `test(mp3): add roundtrip test for metadata write/read`
- `fix(#482): handle null search values`
- `style: format code with ruff`
- `ci: use PAT for auto-approve workflow instead of GITHUB_TOKEN`

##### PR Description

When opening a Pull Request, a template will be automatically provided. Ensure your PR description includes:

- ✅ Clear description of changes
- ✅ Reference related issues (e.g., "Fixes #123")
- ✅ Note any breaking changes
- ✅ Include testing instructions if applicable

**Note:** The PR template (`.github/pull_request_template.md`) will guide you through the process and ensure all necessary information is included.

##### Breaking Changes

If your PR includes breaking changes:

- ✅ Breaking changes are clearly documented in the PR description
- ✅ Migration path is provided (if applicable)
- ✅ Breaking changes include proper versioning notes (for maintainers to handle)

##### PR Automations

When you open a Pull Request, several automations will run automatically:

- **Auto-labeling**: Component labels (like `id3v1`, `id3v2`, `vorbis`, `riff`, `cli`, `core`) and some type labels (`documentation`, `test`, `ci`, `dependencies`) are automatically added based on files changed
- **Manual labels**: You should still add type labels (`bug`, `enhancement`, `feature`) and priority labels manually, as these can't be determined from file paths
- **Auto-assignment**: For contributor PRs (not maintainer PRs), reviewers are automatically assigned
- **CI/CD checks**: Automated tests, linting, and type checking run on your PR
- **Welcome message**: First-time contributors receive a welcome message with helpful links

These automations help streamline the review process and ensure consistency across the project.

### 7. Releasing _(For Maintainers)_

Releases are created from the `main` branch.

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

   - Review changes in the `[Unreleased]` section and decide on version number (following Semantic Versioning)
   - Move content from `[Unreleased]` section to new version entry with date (e.g., `## [0.2.3] - 2025-11-17`)
   - Review and consolidate entries if needed (group similar changes, ensure clarity)
   - Leave the `[Unreleased]` section empty (or with a placeholder) for future PRs

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
