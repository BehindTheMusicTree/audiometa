# Working with Multiple Branches (Git Worktrees)

When working on multiple features simultaneously or when you need separate Cursor windows for different branches, use **git worktrees**. This allows you to have multiple working directories for the same repository, each on a different branch.

## Quick Setup (for Cursor)

Use the provided script to create a worktree and open it in a new Cursor window:

```bash
# Create worktree with new branch (always created from main)
./scripts/create-worktree-cursor.sh feature/my-feature

# Create worktree with custom worktree directory name
./scripts/create-worktree-cursor.sh feature/my-feature my-feature-worktree

# Or use git alias (after running once: git config alias.worktree-cursor '!f() { bash scripts/create-worktree-cursor.sh "$@"; }; f')
git worktree-cursor feature/my-feature
```

### What the Script Does

The `create-worktree-cursor.sh` script automates the following main steps:

1. **Validates prerequisites**: Ensures branch doesn't exist, `main` branch exists, and worktree path is available
2. **Creates worktree**: Creates a new git worktree from the `main` branch with your specified branch name
3. **Sets up development environment**: Creates Python virtual environment and installs all dependencies
4. **Opens in Cursor**: Automatically opens the worktree directory in a new Cursor window

**Important**: The script always creates worktrees from the `main` branch to ensure a consistent base for all new branches.

## Manual Setup

```bash
# Create worktree for existing branch
git worktree add ../audiometa-python-feature2 feature/my-feature

# Create worktree with new branch
git worktree add ../audiometa-python-feature2 -b feature/new-feature

# Open in Cursor (macOS)
open -a Cursor ../audiometa-python-feature2
```

## Benefits

- Work on multiple branches simultaneously
- Each Cursor window operates independently
- No need to stash/commit when switching contexts
- Shared git history (same `.git` directory)

## Cleanup

```bash
# Remove worktree when done
git worktree remove ../audiometa-python-feature2
```

## Example Workflow

```bash
# Main repository in ~/audiometa-python (on main branch)
cd ~/audiometa-python

# Create worktree for feature branch
./scripts/create-worktree-cursor.sh feature/add-flac-support

# This creates:
# - New directory: ~/audiometa-python-feature-add-flac-support
# - Opens new Cursor window with that directory
# - Checks out feature/add-flac-support branch

# Now you can work in both windows:
# - Main window: main branch
# - New window: feature/add-flac-support branch

# When done, remove the worktree
git worktree remove ~/audiometa-python-feature-add-flac-support
```

## Listing Worktrees

```bash
# List all worktrees
git worktree list

# Output example:
# /path/to/audiometa-python          abc1234 [main]
# /path/to/audiometa-python-feature2  def5678 [feature/my-feature]
```

## Notes

- Each worktree shares the same `.git` directory, so commits, branches, and remotes are shared
- You cannot check out the same branch in multiple worktrees simultaneously
- Worktrees are useful for comparing branches side-by-side or working on multiple features without switching contexts
