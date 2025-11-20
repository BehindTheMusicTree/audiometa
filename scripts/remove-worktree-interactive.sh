#!/bin/bash

# Script to list all git worktrees and remove the selected one
#
# This script displays all available git worktrees, allows you to select one,
# and removes it along with its associated branch. Useful for cleaning up
# worktrees interactively.
#
# Usage: ./scripts/remove-worktree-interactive.sh [--remove-remote]

set -e

# Source shared Cursor utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/cursor-common.sh"

# Parse arguments
REMOVE_REMOTE=false
for arg in "$@"; do
    case $arg in
        --remove-remote)
            REMOVE_REMOTE=true
            shift
            ;;
        *)
            echo "Usage: $0 [--remove-remote]"
            echo ""
            echo "Options:"
            echo "  --remove-remote  Also remove remote branches when removing worktrees"
            exit 1
            ;;
    esac
done

# Get the repository root (where .git directory is)
REPO_ROOT=$(git rev-parse --show-toplevel)

# Get all worktrees
WORKTREES=$(git worktree list --porcelain)

if [ -z "$WORKTREES" ]; then
    echo "No worktrees found."
    exit 1
fi

# Parse worktrees into arrays
declare -a PATHS
declare -a BRANCHES

CURRENT_PATH=""
CURRENT_BRANCH=""

while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines
    if [ -z "$line" ]; then
        # Empty line indicates end of current worktree entry
        if [ -n "$CURRENT_PATH" ]; then
            PATHS+=("$CURRENT_PATH")
            BRANCHES+=("$CURRENT_BRANCH")
            CURRENT_PATH=""
            CURRENT_BRANCH=""
        fi
        continue
    fi

    if [[ $line == worktree* ]]; then
        # Save previous worktree if exists
        if [ -n "$CURRENT_PATH" ]; then
            PATHS+=("$CURRENT_PATH")
            BRANCHES+=("$CURRENT_BRANCH")
        fi
        # Extract path (everything after "worktree ")
        CURRENT_PATH="${line#worktree }"
        CURRENT_BRANCH=""
    elif [[ $line == branch* ]]; then
        # Extract branch (everything after "branch refs/heads/")
        BRANCH_REF="${line#branch }"
        CURRENT_BRANCH="${BRANCH_REF#refs/heads/}"
    fi
done <<< "$WORKTREES"

# Save last worktree if exists
if [ -n "$CURRENT_PATH" ]; then
    PATHS+=("$CURRENT_PATH")
    BRANCHES+=("$CURRENT_BRANCH")
fi

# Display worktrees
echo "Available worktrees:"
echo ""
for i in "${!PATHS[@]}"; do
    BRANCH_INFO=""
    if [ -n "${BRANCHES[$i]}" ]; then
        BRANCH_INFO=" [${BRANCHES[$i]}]"
    else
        BRANCH_INFO=" (detached HEAD)"
    fi
    echo "  $((i + 1)). ${PATHS[$i]}${BRANCH_INFO}"
done
echo ""

# Get user selection
read -p "Select worktree to remove (1-${#PATHS[@]}): " SELECTION

# Handle empty input or Ctrl+C
if [ -z "$SELECTION" ]; then
    echo "Error: No selection made"
    exit 1
fi

# Validate selection
if ! [[ "$SELECTION" =~ ^[0-9]+$ ]] || [ "$SELECTION" -lt 1 ] || [ "$SELECTION" -gt "${#PATHS[@]}" ]; then
    echo "Error: Invalid selection. Please enter a number between 1 and ${#PATHS[@]}"
    exit 1
fi

# Get selected worktree path and branch
SELECTED_INDEX=$((SELECTION - 1))
SELECTED_PATH="${PATHS[$SELECTED_INDEX]}"
SELECTED_BRANCH="${BRANCHES[$SELECTED_INDEX]}"

# Convert to absolute path if relative
if [[ ! "$SELECTED_PATH" = /* ]]; then
    SELECTED_PATH=$(cd "$REPO_ROOT" && cd "$SELECTED_PATH" && pwd)
else
    SELECTED_PATH=$(cd "$SELECTED_PATH" && pwd)
fi

# Confirm removal
echo ""
echo "Selected worktree: $SELECTED_PATH"
if [ -n "$SELECTED_BRANCH" ]; then
    echo "Branch: $SELECTED_BRANCH"
else
    echo "Branch: (detached HEAD - no branch to remove)"
fi
echo ""

if [ -z "$SELECTED_BRANCH" ]; then
    read -p "Remove this worktree? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    echo ""
    echo "Removing worktree..."
    git worktree remove "$SELECTED_PATH" --force 2>/dev/null || {
        echo "Warning: Could not remove worktree via git (may not be registered)"
        echo "Removing directory manually..."
        rm -rf "$SELECTED_PATH"
    }
    echo "✓ Worktree removed"
else
    REMOTE_FLAG=""
    if [ "$REMOVE_REMOTE" = true ]; then
        REMOTE_FLAG="--remove-remote"
    elif git show-ref --verify --quiet "refs/remotes/origin/$SELECTED_BRANCH" 2>/dev/null; then
        read -p "Also remove remote branch 'origin/$SELECTED_BRANCH'? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            REMOTE_FLAG="--remove-remote"
        fi
    fi

    echo ""
    "$SCRIPT_DIR/remove-worktree-branch.sh" "$SELECTED_BRANCH" "$SELECTED_PATH" $REMOTE_FLAG
fi

echo ""
echo "✓ Removal complete"
