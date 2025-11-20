#!/bin/bash

# Script to create a git worktree and open it in a new Cursor window

# Usage: ./scripts/create-worktree-cursor.sh <branch-name> [worktree-name]

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <branch-name> [worktree-name]"
    echo ""
    echo "Examples:"
    echo "  $0 feature/my-feature"
    echo "  $0 feature/my-feature my-feature-worktree"
    echo "  $0 -b feature/new-feature new-feature-worktree"
    exit 1
fi

# Get the repository root (where .git directory is)
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")

# Parse arguments
CREATE_BRANCH=false
if [ "$1" = "-b" ]; then
    CREATE_BRANCH=true
    BRANCH_NAME="$2"
    WORKTREE_NAME="${3:-${BRANCH_NAME#feature/}}"
    WORKTREE_NAME="${WORKTREE_NAME#chore/}"
    WORKTREE_NAME="${WORKTREE_NAME#hotfix/}"
else
    BRANCH_NAME="$1"
    WORKTREE_NAME="${2:-${BRANCH_NAME#feature/}}"
    WORKTREE_NAME="${WORKTREE_NAME#chore/}"
    WORKTREE_NAME="${WORKTREE_NAME#hotfix/}"
fi

# Default worktree name if still empty
if [ -z "$WORKTREE_NAME" ]; then
    WORKTREE_NAME="worktree-$(date +%s)"
fi

# Create worktree directory path (sibling to repo)
WORKTREE_PATH="../${REPO_NAME}-${WORKTREE_NAME}"

# Check if worktree already exists
if [ -d "$WORKTREE_PATH" ]; then
    echo "Error: Worktree already exists at $WORKTREE_PATH"
    echo "Remove it first with: git worktree remove $WORKTREE_PATH"
    exit 1
fi

# Check if branch already exists (unless creating new branch)
if [ "$CREATE_BRANCH" = false ]; then
    if ! git show-ref --verify --quiet "refs/heads/$BRANCH_NAME" && ! git show-ref --verify --quiet "refs/remotes/origin/$BRANCH_NAME"; then
        echo "Error: Branch '$BRANCH_NAME' does not exist locally or remotely"
        echo "Use '-b' flag to create a new branch: $0 -b $BRANCH_NAME"
        exit 1
    fi
fi

# Create worktree
echo "Creating worktree for branch: $BRANCH_NAME"
if [ "$CREATE_BRANCH" = true ]; then
    git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME"
else
    git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"
fi

# Get absolute path
WORKTREE_ABS_PATH=$(cd "$WORKTREE_PATH" && pwd)

echo ""
echo "✓ Worktree created at: $WORKTREE_ABS_PATH"
echo ""

# Check and create virtual environment if needed
if [ ! -d "$WORKTREE_ABS_PATH/.venv" ]; then
    echo "Creating virtual environment..."
    cd "$WORKTREE_ABS_PATH"
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -e ".[dev]"
    echo "✓ Virtual environment created and dependencies installed"
    echo ""
else
    echo "Virtual environment already exists at $WORKTREE_ABS_PATH/.venv"
    echo ""
fi

# Open in Cursor (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -d "/Applications/Cursor.app" ]; then
        echo "Opening in Cursor..."
        open -a Cursor "$WORKTREE_ABS_PATH"
    else
        echo "Warning: Cursor.app not found in /Applications"
        echo "Worktree is ready at: $WORKTREE_ABS_PATH"
        echo "Open it manually in Cursor"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v cursor &> /dev/null; then
        echo "Opening in Cursor..."
        cursor "$WORKTREE_ABS_PATH" &
    else
        echo "Warning: 'cursor' command not found"
        echo "Worktree is ready at: $WORKTREE_ABS_PATH"
        echo "Open it manually in Cursor"
    fi
else
    echo "Worktree is ready at: $WORKTREE_ABS_PATH"
    echo "Open it manually in Cursor"
fi

echo ""
echo "To remove this worktree later:"
echo "  git worktree remove $WORKTREE_PATH"
