#!/bin/bash

# Script to create a git worktree from main and open it in a code editor (Cursor or VS Code)
#
# This script automates the process of creating a new git worktree, setting up the
# development environment, and opening it in your preferred editor (Cursor or VS Code).
# All worktrees are created from the main branch to ensure a consistent base.
#
# Usage: ./scripts/create-worktree.sh <branch-name> [worktree-name]
#
# Main steps:
# 1. Validates prerequisites (branch doesn't exist, main branch exists, worktree path available)
# 2. Pulls latest changes from main branch to ensure up-to-date base
# 3. Creates git worktree from main branch with the new branch name
# 4. Sets up Python virtual environment and installs dependencies
# 5. Opens the worktree directory in your editor (Cursor or VS Code)
#
# Examples:
#   ./scripts/create-worktree.sh feature/my-feature
#   ./scripts/create-worktree.sh feature/123-add-ogg-support
#   ./scripts/create-worktree.sh chore/update-dependencies
#   ./scripts/create-worktree.sh hotfix/critical-metadata-bug

set -e

# Source shared editor utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/editor-common.sh"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <branch-name> [worktree-name]"
    echo ""
    echo "Examples:"
    echo "  $0 feature/my-feature"
    echo "  $0 feature/123-add-ogg-support"
    echo "  $0 chore/update-dependencies"
    echo "  $0 hotfix/critical-metadata-bug"
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

    # Check if branch has commits beyond main
    if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
        BRANCH_COMMIT=$(git rev-parse "$BRANCH_NAME" 2>/dev/null)
        MAIN_COMMIT=$(git rev-parse "origin/main" 2>/dev/null || git rev-parse "main" 2>/dev/null)

        if [ "$BRANCH_COMMIT" != "$MAIN_COMMIT" ]; then
            COMMIT_COUNT=$(git rev-list --count "$MAIN_COMMIT..$BRANCH_NAME" 2>/dev/null || echo "0")
            if [ "$COMMIT_COUNT" -gt 0 ]; then
                echo ""
                echo "⚠️  WARNING: Branch '$BRANCH_NAME' has $COMMIT_COUNT uncommitted work!"
                echo "   Removing it will DELETE this work permanently."
            fi
        fi
    fi

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

        # Check if branch has commits beyond main
        BRANCH_COMMIT=$(git rev-parse "$BRANCH_NAME" 2>/dev/null)
        MAIN_COMMIT=$(git rev-parse "origin/main" 2>/dev/null || git rev-parse "main" 2>/dev/null)

        if [ "$BRANCH_COMMIT" != "$MAIN_COMMIT" ]; then
            COMMIT_COUNT=$(git rev-list --count "$MAIN_COMMIT..$BRANCH_NAME" 2>/dev/null || echo "0")
            if [ "$COMMIT_COUNT" -gt 0 ]; then
                echo "     ⚠️  Has $COMMIT_COUNT uncommitted work - removing will DELETE this work!"
            fi
        fi
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

# Pull latest changes from main branch
echo "Pulling latest changes from main branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Switching to main branch to pull latest changes..."
    git checkout main
fi
git pull origin main
echo "✓ Main branch updated"
echo ""

# Switch back to original branch if needed
if [ "$CURRENT_BRANCH" != "main" ] && [ -n "$CURRENT_BRANCH" ]; then
    git checkout "$CURRENT_BRANCH"
fi

# Create worktree from main
echo "Creating worktree from main for new branch: $BRANCH_NAME"
git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" main

# Get absolute path
WORKTREE_ABS_PATH=$(cd "$WORKTREE_PATH" && pwd)

echo ""
echo "✓ Worktree created at: $WORKTREE_ABS_PATH"
echo ""

# Ensure .vscode/settings.json exists (for editor configuration)
if [ ! -f "$WORKTREE_ABS_PATH/.vscode/settings.json" ]; then
    echo "Setting up editor settings..."
    mkdir -p "$WORKTREE_ABS_PATH/.vscode"
    # Copy settings from repo root if it exists
    if [ -f "$REPO_ROOT/.vscode/settings.json" ]; then
        cp "$REPO_ROOT/.vscode/settings.json" "$WORKTREE_ABS_PATH/.vscode/settings.json"
        echo "✓ Editor settings configured"
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

# Open in editor
if ! open_in_editor "$WORKTREE_ABS_PATH"; then
    echo "Warning: Failed to open editor"
    echo "Worktree is ready at: $WORKTREE_ABS_PATH"
    echo "Open it manually in your editor"
fi

echo ""
echo "To remove this worktree later:"
echo "  $SCRIPT_DIR/remove-worktree-branch.sh $BRANCH_NAME $WORKTREE_PATH"
