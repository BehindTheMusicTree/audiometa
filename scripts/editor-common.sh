#!/bin/bash
# Shared utilities for editor-related scripts (Cursor and VS Code)

# Function to open a directory in a code editor (prompts user to choose)
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

    # Detect available editors
    declare -a AVAILABLE_EDITORS=()
    declare -a EDITOR_COMMANDS=()

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if [ -d "/Applications/Cursor.app" ]; then
            AVAILABLE_EDITORS+=("Cursor")
            EDITOR_COMMANDS+=("open -a Cursor")
        fi
        if [ -d "/Applications/Visual Studio Code.app" ]; then
            AVAILABLE_EDITORS+=("VS Code")
            EDITOR_COMMANDS+=("open -a \"Visual Studio Code\"")
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v cursor &> /dev/null; then
            AVAILABLE_EDITORS+=("Cursor")
            EDITOR_COMMANDS+=("cursor")
        fi
        if command -v code &> /dev/null; then
            AVAILABLE_EDITORS+=("VS Code")
            EDITOR_COMMANDS+=("code")
        fi
    else
        echo "Error: Unsupported operating system"
        return 1
    fi

    # Check if any editors are available
    if [ ${#AVAILABLE_EDITORS[@]} -eq 0 ]; then
        echo "Error: No supported editors found (Cursor or VS Code)"
        return 1
    fi

    # If only one editor is available, use it
    if [ ${#AVAILABLE_EDITORS[@]} -eq 1 ]; then
        echo "Opening in ${AVAILABLE_EDITORS[0]}..."
        eval "${EDITOR_COMMANDS[0]} \"$dir_path\""
        return 0
    fi

    # Multiple editors available - prompt user to choose
    echo "Available editors:"
    for i in "${!AVAILABLE_EDITORS[@]}"; do
        echo "  $((i + 1)). ${AVAILABLE_EDITORS[$i]}"
    done
    echo ""
    read -p "Select editor (1-${#AVAILABLE_EDITORS[@]}): " SELECTION

    # Validate selection
    if ! [[ "$SELECTION" =~ ^[0-9]+$ ]] || [ "$SELECTION" -lt 1 ] || [ "$SELECTION" -gt "${#AVAILABLE_EDITORS[@]}" ]; then
        echo "Error: Invalid selection"
        return 1
    fi

    # Open in selected editor
    SELECTED_INDEX=$((SELECTION - 1))
    echo "Opening in ${AVAILABLE_EDITORS[$SELECTED_INDEX]}..."
    eval "${EDITOR_COMMANDS[$SELECTED_INDEX]} \"$dir_path\""
    return 0
}

# Legacy alias for backwards compatibility
open_in_cursor() {
    open_in_editor "$@"
}
