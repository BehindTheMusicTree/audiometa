# File Organization

## Agent Rules File Location

**All agent rules live in `.claude/rules/` as one `.md` file per concern.** Scope a rule to files with a `paths:` frontmatter list; omit it for rules that always apply.

## Module Structure

- Keep related functionality together
- Use clear, descriptive file names
- Avoid unnecessary module docstrings that just describe the file contents

## Import Organization

- Group imports logically
- Use absolute imports when possible
- Keep imports clean and minimal
