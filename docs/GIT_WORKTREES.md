# Working with Multiple Branches (Git Worktrees)

When working on multiple features simultaneously or when you need separate editor windows for different branches, use **git worktrees**. This allows you to have multiple working directories for the same repository, each on a different branch.

## Quick Setup

Use the provided script to create a worktree and open it in your preferred code editor (Cursor or VS Code):

```bash
# Create worktree with new branch (always created from latest main)
./scripts/create-worktree.sh feature/my-feature

# Create worktree with custom worktree directory name
./scripts/create-worktree.sh feature/my-feature my-feature-worktree

# Or use git alias (after running once: git config alias.worktree '!f() { bash scripts/create-worktree.sh "$@"; }; f')
git worktree feature/my-feature
```

The script will automatically detect and open the worktree in:

- **Cursor** if installed (preferred)
- **VS Code** if Cursor is not available
- Otherwise, it will notify you to open the worktree manually

### What the Script Does

The `create-worktree.sh` script automates the following main steps:

1. **Validates prerequisites**: Ensures branch doesn't exist, `main` branch exists, and worktree path is available
2. **Updates main branch**: Pulls the latest changes from `origin/main` to ensure you have the most recent code
3. **Creates worktree**: Creates a new git worktree from the updated `main` branch with your specified branch name
4. **Sets up development environment**: Creates Python virtual environment and installs all dependencies
5. **Opens in editor**: Automatically opens the worktree directory in Cursor or VS Code

**Important**: The script always creates worktrees from the `main` branch (after pulling the latest changes) to ensure a consistent and up-to-date base for all new branches.

## Opening Existing Worktrees

To quickly open an existing worktree in your editor, use the `open-worktree.sh` script:

```bash
# List all worktrees and open selected one in your editor
./scripts/open-worktree.sh
```

The script will:

1. Display all available worktrees with their branch names
2. Prompt you to select a worktree by number
3. Open the selected worktree directory in Cursor or VS Code (whichever is available)

This is useful when you have multiple worktrees and want to quickly switch between them without manually navigating to their directories.

## Manual Setup

```bash
# Create worktree for existing branch
git worktree add ../audiometa-python-feature2 feature/my-feature

# Create worktree with new branch
git worktree add ../audiometa-python-feature2 -b feature/new-feature

# Open in Cursor (macOS)
open -a Cursor ../audiometa-python-feature2

# Or open in VS Code (macOS)
open -a "Visual Studio Code" ../audiometa-python-feature2

# Or use command line (Linux/macOS)
cursor ../audiometa-python-feature2  # for Cursor
code ../audiometa-python-feature2    # for VS Code
```

## Benefits

- Work on multiple branches simultaneously
- Each Cursor window operates independently
- No need to stash/commit when switching contexts
- Shared git history (same `.git` directory)

## Cleanup

### Interactive Removal

To interactively list and remove worktrees:

```bash
# List all worktrees and remove selected one
./scripts/remove-worktree-interactive.sh

# Also remove remote branch when removing worktree
./scripts/remove-worktree-interactive.sh --remove-remote
```

The script will:

1. Display all available worktrees with their branch names
2. Prompt you to select a worktree by number
3. Show the selected worktree details and ask for confirmation
4. Remove the worktree and its associated branch
5. Optionally remove the remote branch if it exists

### Direct Removal

If you know the branch name, you can remove it directly:

```bash
# Remove worktree and local branch
./scripts/remove-worktree-branch.sh feature/my-feature

# Remove worktree, local branch, and remote branch
./scripts/remove-worktree-branch.sh feature/my-feature --remove-remote
```

### Manual Removal

```bash
# Remove worktree when done
git worktree remove ../audiometa-python-feature2
```

## Example Workflow

```bash
# Main repository in ~/audiometa-python (on main branch)
cd ~/audiometa-python

# Create worktree for feature branch
./scripts/create-worktree.sh feature/add-flac-support

# This script will:
# - Pull latest changes from origin/main
# - Create new directory: ~/audiometa-python-feature-add-flac-support
# - Open new editor window (Cursor or VS Code) with that directory
# - Check out feature/add-flac-support branch from updated main

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

# Interactive script to list and open worktrees in your editor
./scripts/open-worktree.sh
```

## Notes

- Each worktree shares the same `.git` directory, so commits, branches, and remotes are shared
- You cannot check out the same branch in multiple worktrees simultaneously
- Worktrees are useful for comparing branches side-by-side or working on multiple features without switching contexts
