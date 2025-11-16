#!/bin/bash
# Wrapper for mypy that ensures venv mypy is used
# This avoids using system mypy with broken shebang

set -e

# Skip venv check in CI environments
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    mypy --follow-imports=normal "$@"
    exit $?
fi

# Use venv mypy if it exists
if [ -f ".venv/bin/mypy" ]; then
    .venv/bin/mypy --follow-imports=normal "$@"
    exit $?
fi

# Fail if venv doesn't exist
echo "ERROR: Virtual environment not found! Please activate .venv or run: source .venv/bin/activate" >&2
exit 1

