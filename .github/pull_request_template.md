## Description

<!-- Provide a clear and concise description of what this PR does -->

## Related Issues

<!-- Reference related issues (e.g., "Fixes #123", "Closes #456") -->

## Type of Change

<!-- Check all that apply. Note: Auto-labeling will add component labels (id3v1, id3v2, etc.) based on files changed. Please add type/priority labels manually. -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test addition/update
- [ ] CI/CD or infrastructure change

## Pre-PR Checklist

<!-- Ensure all items are completed before submitting -->

### Code Quality

- [ ] Removed commented-out code
- [ ] No hardcoded credentials, API keys, or secrets
- [ ] Ran pre-commit hooks: `pre-commit run --all-files` (includes linting, formatting, type checking, assert statement check, debug statement detection, etc.)

### Tests

- [ ] All tests pass: `pytest`
- [ ] Coverage meets threshold (≥85%): `pytest --cov=audiometa --cov-report=term-missing --cov-fail-under=85`
- [ ] New features have corresponding tests
- [ ] Bug fixes include regression tests

### Documentation

- [ ] Updated docstrings for new functions/classes (only when needed - see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines)
- [ ] Updated README if adding new features or changing behavior
- [ ] Updated CONTRIBUTING.md if changing development workflow
- [ ] Added/updated type hints where appropriate

### Git Hygiene

- [ ] Commit messages follow the [commit message convention](docs/COMMITTING.md)
- [ ] No merge conflicts with target branch
- [ ] Branch is up to date with target branch
- [ ] No accidental commits (large files, secrets, personal configs)

## Breaking Changes

<!-- If this PR includes breaking changes, describe them here and provide migration instructions -->

- [ ] This PR includes breaking changes
- [ ] Breaking changes are clearly documented below
- [ ] Migration path is provided (if applicable)

### Breaking Changes Description

<!-- Describe breaking changes and how users should migrate -->

## Testing Instructions

<!-- Provide instructions for testing this PR, if applicable -->

### How to Test

1.
2.
3.

### Test Results

<!-- If applicable, include test results or screenshots -->

## Additional Context

<!-- Add any other context, screenshots, or information about the PR here -->

## Checklist for Reviewers

<!-- Maintainers: Check these before merging -->

- [ ] Code follows project conventions and style
- [ ] Logic is sound and well-structured
- [ ] Error handling is appropriate
- [ ] CI tests pass on all platforms and Python versions
- [ ] Test coverage is adequate for the changes
- [ ] Public API changes are documented
- [ ] Breaking changes are clearly marked and documented
- [ ] All review comments are addressed
- [ ] No unresolved discussions

---

**Note**: Please ensure all items in the Pre-PR Checklist are completed before requesting review. See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.
