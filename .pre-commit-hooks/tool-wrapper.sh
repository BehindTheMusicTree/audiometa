#!/bin/bash
# Generic wrapper for Python tools that ensures venv tools are used
# This avoids using system tools with broken shebangs
#
# Usage: tool-wrapper.sh <tool-name> [tool-args...]
# Example: tool-wrapper.sh mypy --follow-imports=normal

set -e

TOOL_NAME="$1"
shift

# Skip venv check in CI environments
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    "$TOOL_NAME" "$@"
    exit $?
fi

# Use venv tool if it exists
if [ -f ".venv/bin/$TOOL_NAME" ]; then
    ".venv/bin/$TOOL_NAME" "$@"
    exit $?
fi

# Fail if venv doesn't exist
echo "ERROR: Virtual environment not found! Please activate .venv or run: source .venv/bin/activate" >&2
exit 1

