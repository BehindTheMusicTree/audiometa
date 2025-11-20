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
    echo "Warning: Worktree already exists at $WORKTREE_PATH"
    echo ""
    read -p "Remove existing worktree and branch '$BRANCH_NAME'? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        "$SCRIPT_DIR/remove-worktree-branch.sh" "$BRANCH_NAME" "$WORKTREE_PATH"
        echo ""
    else
        echo "Aborted. To remove manually, run:"
        echo "  $SCRIPT_DIR/remove-worktree-branch.sh $BRANCH_NAME $WORKTREE_PATH"
        exit 1
    fi
fi

# Check if branch already exists
BRANCH_EXISTS_LOCAL=false
BRANCH_EXISTS_REMOTE=false
if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    BRANCH_EXISTS_LOCAL=true
fi
if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH_NAME"; then
    BRANCH_EXISTS_REMOTE=true
fi

if [ "$BRANCH_EXISTS_LOCAL" = true ] || [ "$BRANCH_EXISTS_REMOTE" = true ]; then
    echo "Warning: Branch '$BRANCH_NAME' already exists"
    if [ "$BRANCH_EXISTS_LOCAL" = true ]; then
        echo "  - Local branch exists"
    fi
    if [ "$BRANCH_EXISTS_REMOTE" = true ]; then
        echo "  - Remote branch exists"
    fi
    echo ""
    read -p "Remove existing branch? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        REMOVE_REMOTE_FLAG=""
        if [ "$BRANCH_EXISTS_REMOTE" = true ]; then
            read -p "Also remove remote branch? (y/N): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                REMOVE_REMOTE_FLAG="--remove-remote"
            fi
        fi
        "$SCRIPT_DIR/remove-worktree-branch.sh" "$BRANCH_NAME" "$WORKTREE_PATH" $REMOVE_REMOTE_FLAG
        echo ""
    else
        echo "Aborted. To remove manually, run:"
        echo "  $SCRIPT_DIR/remove-worktree-branch.sh $BRANCH_NAME $WORKTREE_PATH"
        if [ "$BRANCH_EXISTS_REMOTE" = true ]; then
            echo "  # Or with remote: $SCRIPT_DIR/remove-worktree-branch.sh $BRANCH_NAME $WORKTREE_PATH --remove-remote"
        fi
        exit 1
    fi
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

# Ensure .vscode/settings.json exists (for Cursor Pyright configuration)
if [ ! -f "$WORKTREE_ABS_PATH/.vscode/settings.json" ]; then
    echo "Setting up Cursor/VSCode settings..."
    mkdir -p "$WORKTREE_ABS_PATH/.vscode"
    # Copy settings from repo root if it exists
    if [ -f "$REPO_ROOT/.vscode/settings.json" ]; then
        cp "$REPO_ROOT/.vscode/settings.json" "$WORKTREE_ABS_PATH/.vscode/settings.json"
        echo "✓ Cursor settings configured"
    fi
    echo ""
fi

# Check and create virtual environment if needed
if [ ! -d "$WORKTREE_ABS_PATH/.venv" ]; then
    echo "Creating virtual environment..."
    cd "$WORKTREE_ABS_PATH"
    python3.13 -m venv .venv
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
echo "  $SCRIPT_DIR/remove-worktree-branch.sh $BRANCH_NAME $WORKTREE_PATH"
