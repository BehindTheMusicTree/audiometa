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
    COMMIT_COUNT=0
    if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
        BRANCH_COMMIT=$(git rev-parse "$BRANCH_NAME" 2>/dev/null)
        MAIN_COMMIT=$(git rev-parse "origin/main" 2>/dev/null || git rev-parse "main" 2>/dev/null)

        if [ "$BRANCH_COMMIT" != "$MAIN_COMMIT" ]; then
            COMMIT_COUNT=$(git rev-list --count "$MAIN_COMMIT..$BRANCH_NAME" 2>/dev/null || echo "0")
        fi
    fi

    echo ""
    if [ "$COMMIT_COUNT" -gt 0 ]; then
        echo "⚠️  WARNING: Branch '$BRANCH_NAME' has $COMMIT_COUNT commit(s) not in main!"
        echo "   Removing it will DELETE this work permanently."
        echo ""
    else
        echo "Branch '$BRANCH_NAME' has 0 commits (freshly created or already merged)"
        echo ""
    fi
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
CREATE_FOR_EXISTING_BRANCH=false
if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    BRANCH_EXISTS_LOCAL=true
fi
if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH_NAME"; then
    BRANCH_EXISTS_REMOTE=true
fi

if [ "$BRANCH_EXISTS_LOCAL" = true ] || [ "$BRANCH_EXISTS_REMOTE" = true ]; then
    echo "Warning: Branch '$BRANCH_NAME' already exists"
    COMMIT_COUNT=0
    HAS_COMMITS=false
    if [ "$BRANCH_EXISTS_LOCAL" = true ]; then
        echo "  - Local branch exists"

        # Check if branch has commits beyond main
        BRANCH_COMMIT=$(git rev-parse "$BRANCH_NAME" 2>/dev/null)
        MAIN_COMMIT=$(git rev-parse "origin/main" 2>/dev/null || git rev-parse "main" 2>/dev/null)

        if [ "$BRANCH_COMMIT" != "$MAIN_COMMIT" ]; then
            COMMIT_COUNT=$(git rev-list --count "$MAIN_COMMIT..$BRANCH_NAME" 2>/dev/null || echo "0")
            if [ "$COMMIT_COUNT" -gt 0 ]; then
                HAS_COMMITS=true
                echo "     ⚠️  Has $COMMIT_COUNT commit(s) - removing will DELETE this work!"
            fi
        fi
    fi
    if [ "$BRANCH_EXISTS_REMOTE" = true ]; then
        echo "  - Remote branch exists"
        # Check remote branch commits if local doesn't have commits
        if [ "$HAS_COMMITS" = false ] && [ "$BRANCH_EXISTS_LOCAL" = false ]; then
            REMOTE_BRANCH_COMMIT=$(git rev-parse "origin/$BRANCH_NAME" 2>/dev/null)
            MAIN_COMMIT=$(git rev-parse "origin/main" 2>/dev/null || git rev-parse "main" 2>/dev/null)
            if [ "$REMOTE_BRANCH_COMMIT" != "$MAIN_COMMIT" ]; then
                COMMIT_COUNT=$(git rev-list --count "$MAIN_COMMIT..origin/$BRANCH_NAME" 2>/dev/null || echo "0")
                if [ "$COMMIT_COUNT" -gt 0 ]; then
                    HAS_COMMITS=true
                    echo "     ⚠️  Has $COMMIT_COUNT commit(s) - removing will DELETE this work!"
                fi
            fi
        fi
    fi
    echo ""

    # Offer to checkout/create worktree if branch has commits
    if [ "$HAS_COMMITS" = true ]; then
        # Check if worktree exists for this branch
        WORKTREE_LIST=$(git worktree list --porcelain 2>/dev/null || echo "")
        EXISTING_WORKTREE=""
        if [ -n "$WORKTREE_LIST" ]; then
            CURRENT_PATH=""
            while IFS= read -r line || [ -n "$line" ]; do
                if [[ $line == worktree* ]]; then
                    CURRENT_PATH="${line#worktree }"
                elif [[ $line == branch* ]]; then
                    BRANCH_REF="${line#branch }"
                    CURRENT_BRANCH="${BRANCH_REF#refs/heads/}"
                    if [ "$CURRENT_BRANCH" = "$BRANCH_NAME" ]; then
                        EXISTING_WORKTREE="$CURRENT_PATH"
                        break
                    fi
                fi
                # Empty line resets for next worktree
                if [ -z "$line" ]; then
                    CURRENT_PATH=""
                fi
            done <<< "$WORKTREE_LIST"
        fi

        if [ -n "$EXISTING_WORKTREE" ]; then
            echo "💡 This branch has existing commits and a worktree already exists."
            echo "   Worktree location: $EXISTING_WORKTREE"
            echo ""
            read -p "Open existing worktree? (Y/n): " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                if open_in_editor "$EXISTING_WORKTREE"; then
                    echo "✓ Worktree opened"
                    exit 0
                else
                    echo "Failed to open worktree. You can open it manually:"
                    echo "  $SCRIPT_DIR/open-worktree.sh"
                    exit 1
                fi
            fi
        else
            echo "💡 This branch has existing commits. What would you like to do?"
            echo ""
            echo "  1) Create worktree for existing branch (recommended)"
            echo "  2) Checkout branch in current repo"
            echo "  3) Remove existing branch"
            echo ""
            read -p "Choose option (1-3) [1]: " -n 1 -r
            echo ""

            if [[ $REPLY =~ ^[23]$ ]]; then
                if [[ $REPLY =~ ^2$ ]]; then
                    # Checkout in current repo
                    echo "Checking out branch '$BRANCH_NAME'..."
                    if [ "$BRANCH_EXISTS_LOCAL" = true ]; then
                        git checkout "$BRANCH_NAME"
                    elif [ "$BRANCH_EXISTS_REMOTE" = true ]; then
                        git checkout -b "$BRANCH_NAME" "origin/$BRANCH_NAME"
                    fi
                    echo "✓ Branch checked out"
                    exit 0
                else
                    # Remove branch (option 3)
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
                    # Continue to create new worktree
                fi
            else
                # Default: Create worktree for existing branch (option 1 or default)
                echo "Creating worktree for existing branch '$BRANCH_NAME'..."
                CREATE_FOR_EXISTING_BRANCH=true
                # Continue to worktree creation below
            fi
        fi
    else
        # No commits, just ask if they want to remove
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
fi

# Ensure main branch exists
if ! git show-ref --verify --quiet "refs/heads/main" && ! git show-ref --verify --quiet "refs/remotes/origin/main"; then
    echo "Error: 'main' branch does not exist locally or remotely"
    exit 1
fi

# Pull latest changes from main branch (only if creating new branch)
if [ "$CREATE_FOR_EXISTING_BRANCH" != true ]; then
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
fi

# Create worktree
if [ "$CREATE_FOR_EXISTING_BRANCH" = true ]; then
    echo "Creating worktree for existing branch: $BRANCH_NAME"
    # Ensure branch exists locally (fetch if remote-only)
    if [ "$BRANCH_EXISTS_LOCAL" = false ] && [ "$BRANCH_EXISTS_REMOTE" = true ]; then
        echo "Fetching branch from remote..."
        git fetch origin "$BRANCH_NAME:$BRANCH_NAME" 2>/dev/null || true
    fi
    # Create worktree and checkout existing branch
    git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"
else
    echo "Creating worktree from main for new branch: $BRANCH_NAME"
    git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" main
fi

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

    # Detect highest available Python version (3.14, 3.13, or 3.12)
    PYTHON_CMD=""
    for version in 3.14 3.13 3.12; do
        if command -v "python${version}" >/dev/null 2>&1; then
            PYTHON_CMD="python${version}"
            break
        fi
    done

    # Fallback to python3 if specific versions not found
    if [ -z "$PYTHON_CMD" ]; then
        if command -v python3 >/dev/null 2>&1; then
            PYTHON_CMD="python3"
        else
            echo "Error: No Python 3.12+ installation found"
            echo "Please install Python 3.12, 3.13, or 3.14"
            exit 1
        fi
    fi

    echo "Using $PYTHON_CMD for virtual environment"
    "$PYTHON_CMD" -m venv .venv
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
