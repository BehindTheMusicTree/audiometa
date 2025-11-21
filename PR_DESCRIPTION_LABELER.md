## Description

This PR fixes the auto-labeler workflow that was failing with the error:

```
Error: found unexpected type for label 'id3v1' (should be array of config options)
```

### Changes

Updated `.github/labeler.yml` to match labeler v5 format requirements:

- Changed from direct file patterns to configuration options with `changed-files` key
- Each label now uses `any-glob-to-any-file` matcher
- Updated all component labels (id3v1, id3v2, vorbis, riff, cli, core, metadata)
- Updated all type labels (documentation, test, ci, dependencies)

### Previous Format (v4 and earlier)

```yaml
id3v1:
  - audiometa/manager/id3v1/**/*
  - audiometa/utils/id3v1_genre_code_map.py
```

### New Format (v5)

```yaml
id3v1:
  - changed-files:
      - any-glob-to-any-file:
          - audiometa/manager/id3v1/**/*
          - audiometa/utils/id3v1_genre_code_map.py
```

## Related Issues

Fixes the auto-labeler workflow failure that occurs on every PR since the labeler was upgraded to v5.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test addition/update
- [x] CI/CD or infrastructure change

## Pre-PR Checklist

### Code Quality

- [x] Removed commented-out code
- [x] No hardcoded credentials, API keys, or secrets
- [x] Ran pre-commit hooks: `pre-commit run --all-files` (includes linting, formatting, type checking, assert statement check, debug statement detection, etc.)

### Tests

- [x] All tests pass: `pytest` (N/A - configuration file only)
- [x] Coverage meets threshold (≥85%): `pytest --cov=audiometa --cov-report=term-missing --cov-fail-under=85` (N/A)
- [x] New features have corresponding tests (N/A - configuration file only)
- [x] Bug fixes include regression tests (N/A - will be verified when PR is created)

### Documentation

- [x] Updated docstrings for new functions/classes (N/A - configuration file only)
- [x] Updated README if adding new features or changing behavior (N/A)
- [x] Updated CONTRIBUTING.md if changing development workflow (N/A)
- [x] Added/updated type hints where appropriate (N/A - YAML file)

### Git Hygiene

- [x] Commit messages follow the [commit message convention](docs/COMMITTING.md)
- [x] No merge conflicts with target branch
- [x] Branch is up to date with target branch
- [x] No accidental commits (large files, secrets, personal configs)

## Breaking Changes

- [ ] This PR includes breaking changes
- [ ] Breaking changes are clearly documented below
- [ ] Migration path is provided (if applicable)

### Breaking Changes Description

<!-- None -->

## Testing Instructions

### How to Test

The fix can only be fully tested by creating a PR and verifying the labeler workflow runs successfully:

1. Create a PR from this branch
2. Check the "Actions" tab for the "Label PRs" workflow
3. Verify the workflow completes successfully without errors
4. Verify that appropriate labels are automatically applied based on files changed

### Expected Behavior

- ✅ Labeler workflow should complete without errors
- ✅ PRs should be automatically labeled based on changed files:
  - Component labels: `id3v1`, `id3v2`, `vorbis`, `riff`, `cli`, `core`, `metadata`
  - Type labels: `documentation`, `test`, `ci`, `dependencies`

## Additional Context

**Background**: The auto-labeling feature was added in v0.2.7 (November 12, 2025) using the old labeler v4 format. When GitHub Actions upgraded to labeler v5, the old format became incompatible, causing workflow failures.

**Why this matters**: Auto-labeling helps maintainers quickly identify what areas of the codebase a PR affects, making code review more efficient.

## Checklist for Reviewers

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

**Note**: This is a critical CI fix that resolves the labeler workflow failure affecting all PRs. The configuration has been updated to match labeler v5 format requirements.
