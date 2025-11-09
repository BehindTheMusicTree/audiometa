#!/bin/bash

# Git Progressive Push Script
#
# This script addresses GitHub's file size limitations by pushing changes progressively
# instead of attempting to push all files at once. This is particularly important for
# audio files which can be large and may exceed GitHub's push size limits.
#
# The script works by:
# 1. Getting a randomized list of modified files
# 2. Processing files one by one
# 3. Committing and pushing each file individually
# 4. Repeating until all files are processed
#
# This approach prevents "remote: error: File is too large" errors when pushing
# large audio files or many files simultaneously to GitHub.

# Check if the commit message is passed as an argument
if [ $# -eq 0 ]; then
    echo "ERROR: please provide a commit message as an argument." >&2
    exit 1
fi

commit_message=$1

# Main loop: continue until all files are processed
while true; do
    # Get a randomized list of modified files to avoid processing files in the same order
    # This randomization helps distribute large files across multiple commits
    IFS=$'\n'
    files=($(git status --porcelain | awk 'BEGIN{srand()} {print rand() "\t" $0}' | sort -n | cut -f2-))

    # Check if the file list is empty (all files have been processed)
    if [ ${#files[@]} -eq 0 ]; then
        echo "No files to add. Ending script."
        break
    fi

    # Process each file individually to avoid hitting GitHub's push size limits
    for file in "${files[@]}"; do
        # Parse git status output to get file status and path
        status=$(echo "$file" | awk '{print $1}')
        file_path=$(echo "$file" | awk '{print substr($0, index($0,$2))}')
        file_path=${file_path%\"}
        file_path=${file_path#\"}

        if [ -n "$file_path" ]; then
            # Handle different file states (deleted, untracked, modified)
            if [ "$status" == "D" ]; then
                # File was deleted - remove from git index
                if git ls-files --error-unmatch "$file_path" >/dev/null 2>&1; then
                    git rm --cached "$file_path"
                fi
            elif [ "$status" == "??" ]; then
                # New untracked file - add to git index
                git add "$file_path"
            else
                # Modified file - add to git index
                git add "$file_path"
            fi

            # Commit and push immediately after adding each file
            # This ensures we never try to push too much data at once
            git commit -m "$commit_message"
            git push
        fi
    done
done
