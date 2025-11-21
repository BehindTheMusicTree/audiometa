#!/bin/bash

# Script to list all git worktrees and remove the selected one
#
# This script displays all available git worktrees, allows you to select one,
# and removes the worktree and its branch (except 'main').
# Useful for cleaning up worktrees interactively.
#
# Behavior:
# 1. Lists all worktrees, marking 'main' branch worktrees as [PROTECTED] and non-selectable
# 2. User selects a worktree by number (only non-main worktrees are numbered)
# 3. Checks and displays merge status of the reference branch (currently checked out branch) to detect safety
#    Safety means: reference branch is merged into origin/main (directly or transitively via regular merges)
#    Merge status is shown to the user before deletion confirmation
#
# If branch is merged (PR accepted):
# 4a. Requires simple 'y/N' confirmation for local branch deletion (safe - work is already in main)
# 5a. If remote branch exists: prompts with 'y/N' for remote branch deletion
#
# If branch is not merged (or merge status unclear):
# 4b. Requires typing 'DELETE' to confirm local branch deletion (destructive operation)
# 5b. If remote branch exists: requires typing 'DELETE' to confirm remote branch deletion
#     Shows merge status and safety information before prompting

# 6. Removes worktree directory and deletes the branch (local and optionally remote) if confirmed
#
# Merge detection (for the reference branch currently checked out in the worktree):
# - Detects if the reference branch is merged directly into origin/main
# - Detects transitive merges (A→B→main) when regular merge commits are used
# - Does NOT detect squash merges (commits are recreated, not preserved in history)
#   If a branch was merged via squash, it won't be detected as merged, but the
#   work is still in main, so it's safe to delete (user decides based on context)
#
# Usage: ./scripts/remove-worktree-interactive.sh

set -e

# Source shared editor utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/editor-common.sh"

# Check for unexpected arguments
if [ $# -gt 0 ]; then
    echo "Usage: $0"
    echo ""
    echo "This script takes no arguments. It will prompt for all confirmations interactively."
    exit 1
fi

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

# Separate worktrees into selectable (non-main) and non-selectable (main)
declare -a SELECTABLE_PATHS
declare -a SELECTABLE_BRANCHES
declare -a SELECTABLE_INDICES

for i in "${!PATHS[@]}"; do
    if [ "${BRANCHES[$i]}" != "main" ]; then
        SELECTABLE_PATHS+=("${PATHS[$i]}")
        SELECTABLE_BRANCHES+=("${BRANCHES[$i]}")
        SELECTABLE_INDICES+=("$i")
    fi
done

# Check if any selectable worktrees exist
if [ ${#SELECTABLE_PATHS[@]} -eq 0 ]; then
    echo "No removable worktrees found."
    echo "(All worktrees have 'main' branch which is protected)"
    exit 0
fi

# Display worktrees: first selectable (non-main), then non-selectable (main)
echo "Available worktrees:"
echo ""

# First, display selectable worktrees (non-main) with numbers
SELECTABLE_NUM=1
for i in "${!PATHS[@]}"; do
    if [ "${BRANCHES[$i]}" != "main" ]; then
        BRANCH_INFO=""
        if [ -n "${BRANCHES[$i]}" ]; then
            BRANCH_INFO=" [${BRANCHES[$i]}]"
        else
            BRANCH_INFO=" (detached HEAD)"
        fi
        echo "  $SELECTABLE_NUM. ${PATHS[$i]}${BRANCH_INFO}"
        SELECTABLE_NUM=$((SELECTABLE_NUM + 1))
    fi
done

# Then, display non-selectable worktrees (main) with [PROTECTED] marker
for i in "${!PATHS[@]}"; do
    if [ "${BRANCHES[$i]}" = "main" ]; then
        BRANCH_INFO=""
        if [ -n "${BRANCHES[$i]}" ]; then
            BRANCH_INFO=" [${BRANCHES[$i]}]"
        else
            BRANCH_INFO=" (detached HEAD)"
        fi
        echo "  [PROTECTED] ${PATHS[$i]}${BRANCH_INFO} (cannot be selected - main branch is protected)"
    fi
done
echo ""

# Get user selection (only selectable worktrees are numbered)
read -p "Select worktree to remove (1-${#SELECTABLE_PATHS[@]}): " SELECTION

# Handle empty input or Ctrl+C
if [ -z "$SELECTION" ]; then
    echo "Error: No selection made"
    exit 1
fi

# Validate selection
if ! [[ "$SELECTION" =~ ^[0-9]+$ ]] || [ "$SELECTION" -lt 1 ] || [ "$SELECTION" -gt "${#SELECTABLE_PATHS[@]}" ]; then
    echo "Error: Invalid selection. Please enter a number between 1 and ${#SELECTABLE_PATHS[@]}"
    exit 1
fi

# Get selected worktree path and currently checked out branch
# Note: Git doesn't track the "original" branch a worktree was created with.
# We only get the branch currently checked out in that worktree.
# If the user checked out different branches over time, we only see the current one.
SELECTED_INDEX=$((SELECTION - 1))
SELECTED_PATH="${SELECTABLE_PATHS[$SELECTED_INDEX]}"
SELECTED_BRANCH="${SELECTABLE_BRANCHES[$SELECTED_INDEX]}"

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

# Note: Worktrees with 'main' branch are filtered out and not selectable
# All remaining worktrees can have their branches deleted

if [ -z "$SELECTED_BRANCH" ]; then
    # Detached HEAD - only remove worktree
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
    # Check merge status first to determine confirmation level
    # Fetch latest origin/main to ensure accurate merge detection
    IS_MERGED=false
    if git fetch origin main --quiet 2>/dev/null; then
        # Check if branch is merged into origin/main (handles direct and transitive regular merges)
        if git merge-base --is-ancestor "$SELECTED_BRANCH" "origin/main" 2>/dev/null; then
            IS_MERGED=true
        fi
    fi

    # Show information about what will be deleted
    echo ""
    if [ "$IS_MERGED" = true ]; then
        echo "ℹ️  Branch '$SELECTED_BRANCH' is merged into origin/main (PR accepted)"
        echo "   Safe to delete - the work is already in main"
    else
        echo "⚠️  WARNING: This operation is DESTRUCTIVE!"
        echo "   Branch '$SELECTED_BRANCH' may not be merged into origin/main"
    fi
    echo ""
    echo "The following will be deleted:"
    echo "  - Local branch: $SELECTED_BRANCH"
    if git show-ref --verify --quiet "refs/remotes/origin/$SELECTED_BRANCH" 2>/dev/null; then
        echo "  - Remote branch: origin/$SELECTED_BRANCH (you will be prompted separately)"
    fi
    echo "  - Worktree directory: $SELECTED_PATH"
    echo ""

    # Require different confirmation based on merge status
    if [ "$IS_MERGED" = true ]; then
        read -p "Delete merged branch? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 1
        fi
    else
        read -p "Type 'DELETE' to confirm branch deletion (or 'N' to abort): " CONFIRMATION
        echo ""
        if [ "$CONFIRMATION" != "DELETE" ]; then
            echo "Aborted. Unmerged branch deletion requires typing 'DELETE'."
            exit 1
        fi
    fi

    # Check remote branch existence (merge status already checked above)
    REMOTE_EXISTS=false
    if git show-ref --verify --quiet "refs/remotes/origin/$SELECTED_BRANCH" 2>/dev/null; then
        REMOTE_EXISTS=true
    fi

    REMOTE_FLAG=""
    if [ "$REMOTE_EXISTS" = true ]; then
        echo ""
        if [ "$IS_MERGED" = true ]; then
            echo "ℹ️  Remote branch 'origin/$SELECTED_BRANCH' exists and is merged into origin/main"
            echo "   (Includes direct merges and transitive merges via regular merge commits)"
            echo "   Safe to delete - the work is already in main"
            echo ""
            echo "⚠️  Note: Deleting remote branch affects the shared repository"
            read -p "Delete remote branch? (y/N): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                REMOTE_FLAG="--remove-remote"
            else
                echo "Remote branch deletion cancelled."
            fi
        else
            echo "⚠️  Remote branch 'origin/$SELECTED_BRANCH' exists but merge status is unclear"
            echo "   Possible reasons:"
            echo "   - Not merged into origin/main"
            echo "   - Merged via squash/rebase (commits recreated, not detected)"
            echo "   - Part of an open or closed PR"
            echo ""
            echo "   ⚠️  Deleting it may break an open PR or remove unmerged work"
            echo "   (If it was merged via squash, the work is in main but won't be detected)"
            echo ""
            echo "⚠️  WARNING: Deleting remote branch affects the shared repository and may affect others"
            read -p "Type 'DELETE' to confirm remote branch deletion anyway (or 'N' to abort): " REMOTE_CONFIRMATION
            echo ""
            if [ "$REMOTE_CONFIRMATION" = "DELETE" ]; then
                REMOTE_FLAG="--remove-remote"
            else
                echo "Remote branch deletion cancelled."
            fi
        fi
    fi

    echo ""
    "$SCRIPT_DIR/remove-worktree-branch.sh" "$SELECTED_BRANCH" "$SELECTED_PATH" $REMOTE_FLAG
fi

echo ""
echo "✓ Removal complete"
