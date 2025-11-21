## Description

This PR reorganizes and improves the project's documentation structure for better consistency, discoverability, and maintainability. All documentation is now centralized in the `docs/` directory, and major sections have been extracted into dedicated guides.

**Key Changes:**

- Moved test documentation from `audiometa/test/README.md` to `docs/TESTING.md` for consistency
- Created dedicated `docs/COMMITTING.md` guide with comprehensive commit message guidelines
- Reorganized `DEVELOPMENT.md` structure for logical grouping (code quality sections)
- Streamlined `CONTRIBUTING.md` with references to dedicated documentation
- Improved changelog best practices section with clearer structure
- Documented that even maintainers now go through the PR process and don't merge directly to main

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

- [x] All tests pass: `pytest`
- [x] Coverage meets threshold (≥85%): `pytest --cov=audiometa --cov-report=term-missing --cov-fail-under=85`
- [x] New features have corresponding tests
- [x] Bug fixes include regression tests

### Documentation

- [x] Updated docstrings for new functions/classes (only when needed - see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines)
- [x] Updated README if adding new features or changing behavior
- [x] Updated CONTRIBUTING.md if changing development workflow
- [x] Added/updated type hints where appropriate
- [x] Updated CHANGELOG.md with changes

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

N/A - This is a documentation-only change with no breaking changes.

## Testing Instructions

### How to Test

1. Review the new documentation structure:

   - Check `docs/TESTING.md` contains all test documentation
   - Check `docs/COMMITTING.md` contains comprehensive commit guidelines
   - Verify `DEVELOPMENT.md` has logical code quality grouping
   - Verify `CONTRIBUTING.md` references point to correct documentation locations

2. Verify links work correctly:

   - All internal links in `CONTRIBUTING.md` should resolve
   - PR template link to `docs/COMMITTING.md` should work
   - Cross-references between documents should be accurate

3. Check documentation completeness:
   - All information from original locations is preserved
   - No content was lost in the reorganization
   - New structure is more logical and easier to navigate

### Test Results

- All pre-commit hooks pass
- All tests pass
- Documentation links verified
- No broken references

## Additional Context

**Documentation Structure Improvements:**

1. **Centralized Documentation**: All documentation now lives in `docs/` directory for consistency:

   - `docs/TESTING.md` - Comprehensive test documentation (moved from `audiometa/test/README.md`)
   - `docs/COMMITTING.md` - Commit message guide (new)
   - Other guides already in `docs/` (e.g., `METADATA_FIELD_GUIDE.md`, `ERROR_HANDLING_GUIDE.md`)

2. **DEVELOPMENT.md Reorganization**:

   - Grouped all code quality concerns under "Code Quality" section:
     - General Practices
     - Code Style Conventions
     - Docstrings (moved from Documentation - it's code quality, not project docs)
     - Type Checking
     - Known Linting Issues
   - Renamed "Documentation" to "Project Documentation" to clarify it's about documentation files

3. **CONTRIBUTING.md Streamlining**:

   - Shortened Testing section with link to `docs/TESTING.md`
   - Added Pre-PR Checklist as subsection 6.1
   - Added Opening a Pull Request as subsection 6.2
   - Updated all references to point to `docs/` directory

4. **New Dedicated Guides**:

   - `docs/COMMITTING.md`: Comprehensive guide covering commit message format, types, scopes, pre-commit hooks, virtual environment requirements, and examples
   - `docs/TESTING.md`: Enhanced with Windows testing details, CI configuration, and system dependency information

5. **Workflow Standardization**:
   - Documented that even maintainers must go through the PR process and cannot merge directly to main
   - Ensures all changes receive proper review and CI validation

**Benefits:**

- Better discoverability: All documentation in one place
- Logical organization: Related content grouped together
- Easier maintenance: Dedicated guides for specific topics
- Improved contributor experience: Clearer structure and better navigation

## Checklist for Reviewers

<!-- Maintainers: Check these before merging -->

- [x] Code follows project conventions and style
- [x] Logic is sound and well-structured
- [x] Error handling is appropriate
- [ ] CI tests pass on all platforms and Python versions
- [x] Test coverage is adequate for the changes
- [x] Public API changes are documented
- [x] Breaking changes are clearly marked and documented
- [ ] All review comments are addressed
- [ ] No unresolved discussions

---

**Note**: Please ensure all items in the Pre-PR Checklist are completed before requesting review. See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.
