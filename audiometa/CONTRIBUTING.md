# 🧭 Contributing Guidelines

Thank you for your interest in contributing!  
This project is currently maintained by a solo developer, but contributions, suggestions, and improvements are welcome.

## Table of Contents

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
- [🚀 Releasing](#-releasing)
- [🧩 Commit Style](#-commit-style)
- [💡 Contributing Code](#-contributing-code)
- [📦 Environment Setup](#-environment-setup)
- [🪪 License & Attribution](#-license--attribution)
- [🌍 Contact & Discussions](#-contact--discussions)

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

## 🧪 Testing

We use pytest for all automated testing.

### Run Local Tests

```bash
pytest
```

### Run Coverage

#### Running Tests with Coverage

To run tests with coverage (recommended before committing or in CI):

```bash
pytest --cov=audiometa --cov-report=html --cov-report=term-missing --cov-fail-under=85
```

This will:

- Measure coverage for the `audiometa` package
- Display coverage summary in the terminal (including missing lines)
- Generate an HTML report in `htmlcov/` directory
- Fail if coverage is below 85%

#### Running Tests Without Coverage

For faster development cycles, run tests without coverage:

```bash
pytest  # Fast, no coverage overhead
```

#### Viewing Coverage Reports

To view the HTML coverage report:

```bash
open htmlcov/index.html  # macOS
# or open htmlcov/index.html in your browser
```

### Lint Code for Style Consistency

```bash
black . && flake8
```

CI will automatically test all pushes and PRs using GitHub Actions.

## 🚀 Releasing

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

## 🧩 Commit Style

Follow conventional commits for clarity and automated versioning:

- `feat:` → new feature
- `fix:` → bug fix
- `refactor:` → code refactoring
- `docs:` → documentation updates
- `chore:` → dependencies or CI updates

Example:

```
feat(api): improve genre matching accuracy
```

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

## 🪪 License & Attribution

All contributions are made under the project's open-source license.  
You retain authorship of your code; the project retains redistribution rights under the same license.

## 🌍 Contact & Discussions

You can open:

- **Issues** → bug reports or new ideas
- **Discussions** → suggestions, architecture, or music-genre topics

Let's make this library grow together 🌱
