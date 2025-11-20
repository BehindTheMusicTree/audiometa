#!/bin/bash
# Shared utilities for Cursor-related scripts

# Function to open a directory in Cursor
# Usage: open_in_cursor <directory_path>
# Returns 0 on success, 1 on failure
open_in_cursor() {
    local dir_path="$1"

    if [ -z "$dir_path" ]; then
        echo "Error: Directory path is required"
        return 1
    fi

    if [ ! -d "$dir_path" ]; then
        echo "Error: Directory does not exist: $dir_path"
        return 1
    fi

    # Open in Cursor (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ -d "/Applications/Cursor.app" ]; then
            open -a Cursor "$dir_path"
            return 0
        else
            echo "Error: Cursor.app not found in /Applications"
            return 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v cursor &> /dev/null; then
            cursor "$dir_path" &
            return 0
        else
            echo "Error: 'cursor' command not found"
            return 1
        fi
    else
        echo "Error: Unsupported operating system"
        return 1
    fi
}
