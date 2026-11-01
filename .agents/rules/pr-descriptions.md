# Pull Request Description Generation

## User asks for a PR description

When the user asks for a **PR description** (or equivalent: “PR desc”, “description for the PR”, “text for GitHub”):

1. **Always write a separate file** under `.github/pr_descriptions/` — do **not** treat a long chat reply as sufficient. The markdown file is the deliverable; chat should point to it.
2. **Use a descriptive name**: `.github/pr_descriptions/PR_DESCRIPTION_<TOPIC>.md` (e.g. `PR_DESCRIPTION_VORBIS_DISC_READ.md`). Create or overwrite that file with the full template content.
3. **In the chat reply**: give the **path** to the file, the **PR title** line to paste on GitHub, and at most a **short summary** — avoid duplicating the full PR body in chat.

If the user only wants a **title** (no body), a one-line answer in chat is fine; otherwise default to the file workflow above.

## PR Description Format

When generating PR descriptions, create them as **standalone markdown documents** that provide comprehensive context for code reviewers and maintainers.

**When providing a PR description, always generate a PR title as well.** Use the format defined in the [PR Naming Convention](pr-naming.md): `<type>(<optional-scope>): <short imperative description>`.

### Document Structure

1. **Include a PR title** at the top of the document (or clearly stated) so the author can copy it into the GitHub PR title field.
2. **Create or update PR description document** in the `.github/pr_descriptions/` directory (gitignored):
   - Create `.github/pr_descriptions/PR_DESCRIPTION_<TOPIC>.md` (e.g. `.github/pr_descriptions/PR_DESCRIPTION_WORKTREE.md`)
3. **Follow the standard PR template structure** (see sections below)
4. **Be thorough and specific** - reviewers need complete context
5. **Include all checklist items** - track what's been completed

**Note:** The `.github/pr_descriptions/` directory is gitignored (except for `pull_request_template.md`), so PR description files are local reference documents only and won't be committed to the repository. They serve as working documents for creating PR descriptions on GitHub. The `pull_request_template.md` file in this directory is the actual GitHub PR template and is tracked in git.

### Standard PR Template Structure

```markdown
## PR Title

<type>(<optional-scope>): <short imperative description>

## Description

<Clear summary of what changed and why>

**Key Changes/Improvements:**

- <Major change 1>
- <Major change 2>
- <etc.>

## Related Issues

<Issue numbers or "None">

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test addition/update
- [ ] CI/CD or infrastructure change

## Pre-PR Checklist

### Code Quality

- [ ] Removed commented-out code
- [ ] No hardcoded credentials, API keys, or secrets
- [ ] Ran pre-commit hooks: `pre-commit run --all-files`

### Tests

- [ ] All tests pass: `pytest`
- [ ] Coverage meets threshold (≥85%): `pytest --cov=audiometa --cov-report=term-missing --cov-fail-under=85`
- [ ] New features have corresponding tests
- [ ] Bug fixes include regression tests

### Documentation

- [ ] Updated docstrings for new functions/classes (only when needed)
- [ ] Updated README if adding new features or changing behavior
- [ ] Updated CONTRIBUTING.md if changing development workflow
- [ ] Added/updated type hints where appropriate
- [ ] Updated CHANGELOG.md with changes

### Git Hygiene

- [ ] Commit messages follow the [commit message convention](docs/COMMITTING.md)
- [ ] No merge conflicts with target branch
- [ ] Branch is up to date with target branch
- [ ] No accidental commits (large files, secrets, personal configs)

## Breaking Changes

- [ ] This PR includes breaking changes
- [ ] Breaking changes are clearly documented below
- [ ] Migration path is provided (if applicable)

### Breaking Changes Description

<Description or "N/A">

## Testing Instructions

### How to Test

<Step-by-step instructions for testing the changes>

### Test Results

<Summary of test outcomes>

## Additional Context

<Any additional information that helps reviewers understand the changes>

**Benefits:**

- <Benefit 1>
- <Benefit 2>

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
```

## Key Principles

### 1. Be Comprehensive

- **Description**: Explain not just what changed, but **why** it changed
- **Context**: Include relevant background information
- **Impact**: Describe how the changes affect users, developers, or the codebase

### 2. Make Testing Easy

- **Provide clear steps**: Anyone should be able to test the changes
- **Include examples**: Show actual commands or code to run
- **Document expected results**: What should testers see?

### 3. Track Everything

- **Check all applicable items**: Be honest about what's been done
- **Note N/A items**: Explain why certain checklist items don't apply
- **Update checklist**: Mark items as complete when they're done

### 4. Consider Reviewers

- **Highlight key changes**: Use bold text for important points
- **Organize logically**: Group related information together
- **Include references**: Link to related issues, docs, or code

## Type-Specific Guidelines

### Bug Fixes

- **Describe the bug**: What was broken?
- **Explain the fix**: How does the change solve the problem?
- **Include reproduction steps**: How to verify the bug existed
- **Show verification**: How to confirm the fix works
- **Add regression tests**: Ensure the bug doesn't come back

### New Features

- **Describe the feature**: What new capability does this add?
- **Explain the use case**: Why is this needed?
- **Show examples**: How will users use this feature?
- **Document API changes**: New functions, parameters, etc.
- **Include tests**: Demonstrate the feature works correctly

### Documentation Updates

- **Summarize changes**: What documentation was updated?
- **Explain motivation**: Why was the update needed?
- **List affected files**: Which docs changed?
- **Note improvements**: How is the documentation better?

### Refactoring

- **Describe the refactoring**: What code structure changed?
- **Explain benefits**: Why is the new structure better?
- **Confirm no functional changes**: Emphasize behavior is unchanged
- **Show test coverage**: Demonstrate nothing broke

### CI/CD Changes

- **Describe the change**: What workflow/configuration changed?
- **Explain impact**: How does this affect the build/deploy process?
- **Show verification**: How to confirm the change works?
- **Note platform effects**: Does this affect specific environments?

## Common Patterns

### For Script/Tool Changes

```markdown
**Prerequisites:**

- List required tools
- List required environment setup

**Test Steps:**

1. Step-by-step instructions
2. Include actual commands
3. Show expected output
```

### For API Changes

````markdown
**Previous API:**

```python
# Old code example
```
````

**New API:**

```python
# New code example
```

**Migration Path:**

- Step 1
- Step 2

````

### For Breaking Changes

```markdown
## Breaking Changes

- [x] This PR includes breaking changes
- [x] Breaking changes are clearly documented below
- [x] Migration path is provided (if applicable)

### Breaking Changes Description

**What breaks:** <Description>

**Why this change:** <Rationale>

**Migration steps:**
1. <Step 1>
2. <Step 2>

**Example migration:**
```python
# Before
old_code()

# After
new_code()
````

```

## Checklist Item Notes

### When to Mark N/A

- **Tests N/A**: For documentation-only changes, configuration files
- **Coverage N/A**: For shell scripts, CI configs, docs
- **Docstrings N/A**: For scripts, configs, non-Python changes
- **README N/A**: For internal changes that don't affect user-facing behavior
- **Type hints N/A**: For shell scripts, YAML files, docs

### Always Required

- **Pre-commit hooks**: Always run, even for docs
- **Git hygiene**: Always applies
- **CHANGELOG.md**: Always update in the `[Unreleased]` section
- **Commit messages**: Always follow conventions

## Examples

PR description files should be created in `.github/pr_descriptions/` directory:
- `.github/pr_descriptions/PR_DESCRIPTION_WORKTREE.md` - For worktree-related changes
- `.github/pr_descriptions/PR_DESCRIPTION_LABELER.md` - For labeler CI changes
- `.github/pr_descriptions/PR_DESCRIPTION_<TOPIC>.md` - Use descriptive topic names

## Benefits

- **Complete context**: Reviewers understand the full scope of changes
- **Easier reviews**: Clear structure helps reviewers focus on what matters
- **Better tracking**: Checklists ensure nothing is forgotten
- **Documentation**: PR descriptions serve as historical record
- **Consistency**: Standard format across all PRs
```
