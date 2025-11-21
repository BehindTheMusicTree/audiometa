#!/bin/bash

# Script to list all git worktrees and open the selected one in Cursor
#
# This script displays all available git worktrees, allows you to select one,
# and opens it in Cursor. Useful for quickly switching between worktrees.
#
# Usage: ./scripts/open-worktree-cursor.sh

set -e

# Source shared Cursor utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/cursor-common.sh"

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
read -p "Select worktree (1-${#PATHS[@]}): " SELECTION

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

# Get selected worktree path
SELECTED_INDEX=$((SELECTION - 1))
SELECTED_PATH="${PATHS[$SELECTED_INDEX]}"

# Convert to absolute path if relative
if [[ ! "$SELECTED_PATH" = /* ]]; then
    SELECTED_PATH=$(cd "$REPO_ROOT" && cd "$SELECTED_PATH" && pwd)
else
    SELECTED_PATH=$(cd "$SELECTED_PATH" && pwd)
fi

echo ""
echo "Opening: $SELECTED_PATH"
echo ""

# Open in Cursor
if ! open_in_cursor "$SELECTED_PATH"; then
    exit 1
fi
