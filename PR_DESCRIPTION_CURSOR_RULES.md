## Description

Adds comprehensive Cursor rules for standardized generation of GitHub issues and PR descriptions as standalone markdown documents.

**Key Changes:**

1. **GitHub Issue Generation Rules** (separate files for each template type):

   - `.cursor/rules/github-feature-requests.mdc`: Feature Request template format
   - `.cursor/rules/github-bug-reports.mdc`: Bug Report template format
   - Issues formatted as standalone markdown documents with code-wrapped sections for easy copying
   - Includes complete field specifications for each template type (with required/optional indicators, dropdown options)
   - Provides example formats and submission instructions

2. **PR Description Generation Rule** (`.cursor/rules/pr-descriptions.mdc`):
   - Defines standard format for creating comprehensive PR descriptions
   - Includes complete PR template structure with all required sections
   - Provides type-specific guidelines (bug fixes, features, docs, refactoring, CI/CD)
   - Documents when checklist items apply or are N/A
   - Includes examples and best practices for thorough PR documentation

## Related Issues

None

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test addition/update
- [ ] CI/CD or infrastructure change

## Pre-PR Checklist

### Code Quality

- [x] Removed commented-out code
- [x] No hardcoded credentials, API keys, or secrets
- [x] Ran pre-commit hooks: `pre-commit run --all-files` (includes linting, formatting, type checking, assert statement check, debug statement detection, etc.)

### Tests

- [x] All tests pass: `pytest` (N/A - cursor rules only)
- [x] Coverage meets threshold (≥85%): `pytest --cov=audiometa --cov-report=term-missing --cov-fail-under=85` (N/A - cursor rules only)
- [x] New features have corresponding tests (N/A - cursor rules only)
- [x] Bug fixes include regression tests (N/A - cursor rules only)

### Documentation

- [x] Updated docstrings for new functions/classes (N/A - cursor rules only)
- [x] Updated README if adding new features or changing behavior (N/A - workflow rules, not user-facing)
- [x] Updated CONTRIBUTING.md if changing development workflow (N/A - internal rules)
- [x] Added/updated type hints where appropriate (N/A - markdown files)
- [x] Updated CHANGELOG.md with changes

### Git Hygiene

- [x] Commit messages follow the [commit message convention](docs/COMMITTING.md)
- [x] No merge conflicts with target branch
- [x] Branch is up to date with target branch
- [x] No accidental commits (large files, secrets, personal configs)

## Breaking Changes

- [ ] This PR includes breaking changes

## Testing Instructions

### How to Test

**Verify GitHub Issue Rules:**

1. Review `.cursor/rules/github-feature-requests.mdc`:

   - Check it includes complete Feature Request template specifications
   - Verify field order matches actual GitHub template
   - Confirm example format is complete

2. Review `.cursor/rules/github-bug-reports.mdc`:

   - Check it includes complete Bug Report template specifications
   - Verify field order matches actual GitHub template
   - Confirm example format is complete

3. Test by generating a sample issue:
   - Ask AI to generate a GitHub issue using the rule
   - Verify it creates a separate `.md` file
   - Verify sections are wrapped in code blocks
   - Verify all fields are present and properly formatted

**Verify PR Description Rule:**

1. Review `.cursor/rules/pr-descriptions.mdc`:

   - Check it includes complete PR template structure
   - Verify type-specific guidelines are comprehensive
   - Confirm checklist items are accurate
   - Check examples reference existing PR descriptions

2. Test by generating a sample PR description:
   - Ask AI to generate a PR description using the rule
   - Verify it creates or updates a `PR_DESCRIPTION*.md` file
   - Verify all sections are included
   - Verify checklists are properly formatted

### Test Results

✅ Both cursor rules reviewed and verified
✅ Field specifications match actual GitHub templates
✅ Examples are clear and comprehensive
✅ Pre-commit hooks pass

## Additional Context

**Why Separate Files:**

Both rules emphasize creating **standalone markdown documents** rather than inline text:

- **GitHub Issues**: Created as `ISSUE_<TOPIC>.md` files with code-wrapped sections for easy copying to GitHub forms
- **PR Descriptions**: Created as `PR_DESCRIPTION*.md` files with complete template structure

**Benefits:**

- **Easy to copy**: Code-wrapped sections enable clean clipboard copying
- **Clear structure**: Matches GitHub form templates exactly
- **Complete documentation**: All context preserved in one file
- **Reusable**: Can be saved and referenced later
- **Consistency**: Standard format across all issues and PRs
- **Quality**: Ensures comprehensive documentation with proper checklists

**Coverage:**

- **GitHub Issues**: Separate rules for Feature Request and Bug Report templates
- **PR Descriptions**: All PR types covered (bug fixes, features, docs, refactoring, CI/CD)
- **Checklists**: Complete Pre-PR and Reviewer checklists included
- **Examples**: References to existing PR descriptions for guidance

## Checklist for Reviewers

- [x] Code follows project conventions and style (N/A - documentation only)
- [x] Logic is sound and well-structured
- [x] Error handling is appropriate (N/A - documentation only)
- [ ] CI tests pass on all platforms and Python versions (N/A - documentation only)
- [x] Test coverage is adequate for the changes (N/A - documentation only)
- [x] Public API changes are documented (N/A - internal rules)
- [x] Breaking changes are clearly marked and documented (No breaking changes)
- [ ] All review comments are addressed
- [ ] No unresolved discussions

---

**Note**: These cursor rules establish a consistent workflow for creating well-structured GitHub issues and PR descriptions. They complement existing cursor rules for code style, testing, and git workflow.
