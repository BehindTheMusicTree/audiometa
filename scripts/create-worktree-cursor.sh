#!/bin/bash

# Script to create a git worktree from main and open it in a new Cursor window
#
# This script automates the process of creating a new git worktree, setting up the
# development environment, and opening it in Cursor. All worktrees are created
# from the main branch to ensure a consistent base.
#
# Usage: ./scripts/create-worktree-cursor.sh <branch-name> [worktree-name]
#
# Main steps:
# 1. Validates prerequisites (branch doesn't exist, main branch exists, worktree path available)
# 2. Creates git worktree from main branch with the new branch name
# 3. Sets up Python virtual environment and installs dependencies
# 4. Opens the worktree directory in Cursor
#
# Examples:
#   ./scripts/create-worktree-cursor.sh feature/my-feature
#   ./scripts/create-worktree-cursor.sh feature/my-feature my-feature-worktree
#   ./scripts/create-worktree-cursor.sh chore/update-dependencies

set -e

# Source shared Cursor utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/cursor-common.sh"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <branch-name> [worktree-name]"
    echo ""
    echo "Examples:"
    echo "  $0 feature/my-feature"
    echo "  $0 feature/my-feature my-feature-worktree"
    echo "  $0 chore/update-dependencies"
    exit 1
fi

# Get the repository root (where .git directory is)
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")

# Parse arguments
BRANCH_NAME="$1"
WORKTREE_NAME="${2:-${BRANCH_NAME#feature/}}"
WORKTREE_NAME="${WORKTREE_NAME#chore/}"
WORKTREE_NAME="${WORKTREE_NAME#hotfix/}"

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

# Check if branch already exists
if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME" || git show-ref --verify --quiet "refs/remotes/origin/$BRANCH_NAME"; then
    echo "Error: Branch '$BRANCH_NAME' already exists locally or remotely"
    echo "Use a different branch name or delete the existing branch first"
    exit 1
fi

# Ensure main branch exists
if ! git show-ref --verify --quiet "refs/heads/main" && ! git show-ref --verify --quiet "refs/remotes/origin/main"; then
    echo "Error: 'main' branch does not exist locally or remotely"
    exit 1
fi

# Create worktree from main
echo "Creating worktree from main for new branch: $BRANCH_NAME"
git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" main

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

# Open in Cursor
echo "Opening in Cursor..."
if ! open_in_cursor "$WORKTREE_ABS_PATH"; then
    echo "Warning: Failed to open Cursor"
    echo "Worktree is ready at: $WORKTREE_ABS_PATH"
    echo "Open it manually in Cursor"
fi

echo ""
echo "To remove this worktree later:"
echo "  git worktree remove $WORKTREE_PATH"
