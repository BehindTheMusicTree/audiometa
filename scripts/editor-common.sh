#!/bin/bash
# Shared utilities for editor-related scripts (Cursor and VS Code)

# Function to open a directory in a code editor (tries Cursor first, then VS Code)
# Usage: open_in_editor <directory_path>
# Returns 0 on success, 1 on failure
open_in_editor() {
    local dir_path="$1"

    if [ -z "$dir_path" ]; then
        echo "Error: Directory path is required"
        return 1
    fi

    if [ ! -d "$dir_path" ]; then
        echo "Error: Directory does not exist: $dir_path"
        return 1
    fi

    # Try to open in Cursor first, then fall back to VS Code
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if [ -d "/Applications/Cursor.app" ]; then
            echo "Opening in Cursor..."
            open -a Cursor "$dir_path"
            return 0
        elif [ -d "/Applications/Visual Studio Code.app" ]; then
            echo "Opening in VS Code..."
            open -a "Visual Studio Code" "$dir_path"
            return 0
        else
            echo "Error: Neither Cursor.app nor Visual Studio Code.app found in /Applications"
            return 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v cursor &> /dev/null; then
            echo "Opening in Cursor..."
            cursor "$dir_path" &
            return 0
        elif command -v code &> /dev/null; then
            echo "Opening in VS Code..."
            code "$dir_path" &
            return 0
        else
            echo "Error: Neither 'cursor' nor 'code' command found"
            return 1
        fi
    else
        echo "Error: Unsupported operating system"
        return 1
    fi
}

# Legacy alias for backwards compatibility
open_in_cursor() {
    open_in_editor "$@"
}
