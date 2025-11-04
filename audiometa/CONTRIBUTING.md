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
  - [🚀 Releasing](#releasing)
- [📝 Commit Message Convention](#-commit-message-convention)
  - [Format](#format)
    - [Breaking Changes](#breaking-changes)
  - [Example](#example)
  - [Allowed Commit Types](#allowed-commit-types)
  - [Scopes](#scopes)
    - [Common Scopes](#common-scopes)
    - [Test Commits Best Practices](#test-commits-best-practices)
  - [Examples](#examples)
  - [Guidelines](#guidelines)
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

Currently, this project has a solo maintainer, but the role may expand as the project grows.

## 💡 Contributing Code

1. Fork the repository
2. Create a `feature/` branch
3. Run tests locally
4. Open a Pull Request with a clear description

## 📦 Environment Setup

Ensure you're using:

- Python 3.10+
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

### Hotfix Branches (`hotfix/<issue>`)

- For urgent bug fixes on production versions

### 🧪 Testing

We use pytest for all automated testing.

#### Run Local Tests

```bash
pytest
```

#### Run Coverage

##### Running Tests with Coverage

To run tests with coverage (recommended before committing or in CI):

```bash
pytest --cov=audiometa --cov-report=html --cov-report=term-missing --cov-fail-under=85
```

This will:

- Measure coverage for the `audiometa` package
- Display coverage summary in the terminal (including missing lines)
- Generate an HTML report in `htmlcov/` directory
- Fail if coverage is below 85%

##### Running Tests Without Coverage

For faster development cycles, run tests without coverage:

```bash
pytest  # Fast, no coverage overhead
```

##### Viewing Coverage Reports

To view the HTML coverage report:

```bash
open htmlcov/index.html  # macOS
# or open htmlcov/index.html in your browser
```

#### Lint Code for Style Consistency

```bash
black . && flake8
```

CI will automatically test all pushes and PRs using GitHub Actions.

### Commit Message Convention

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

| Scope  | Example                                             | Description                  |
| ------ | --------------------------------------------------- | ---------------------------- |
| core   | refactor(core): simplify metadata interface         | Core metadata handling logic |
| id3v1  | fix(id3v1): handle encoding issues                  | ID3v1 tag format             |
| id3v2  | feat(id3v2): add custom text frame support          | ID3v2 tag format             |
| vorbis | fix(vorbis): improve comment parsing                | Vorbis comment format        |
| riff   | feat(riff): detect and write INFO chunks            | RIFF metadata format         |
| test   | refactor(test): reorganize test fixtures            | Testing infrastructure       |
| io     | test(io): verify metadata persistence on temp files | File I/O operations          |
| deps   | chore(deps): update mutagen dependency              | Dependency management        |
| docs   | docs: improve README example                        | Documentation updates        |

##### Test Commits Best Practices

For a single library project, use `test:` as the **type**, not the scope, for general test changes:

- `test(mp3): add roundtrip test for title tag`
- `test(io): verify temporary file metadata write`
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
test(io): add roundtrip test for metadata write/read
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

### Releasing _(For Maintainers)_

Releases are created from the `main` branch.

1. Bump your version (using bump2version or manually editing **version**)
2. Tag the release:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
3. CI/CD will:
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
