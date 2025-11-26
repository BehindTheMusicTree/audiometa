#!/bin/bash
set -e
WORKTREE_PATH="${1:-$(pwd)}"
cd "$WORKTREE_PATH"

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."

    PYTHON_CMD=""
    for version in 3.14 3.13 3.12; do
        if command -v "python${version}" >/dev/null 2>&1; then
            PYTHON_CMD="python${version}"
            break
        fi
    done

    if [ -z "$PYTHON_CMD" ]; then
        if command -v python3 >/dev/null 2>&1; then
            PYTHON_CMD="python3"
        else
            echo "Warning: No Python 3.12+ installation found"
            exit 0
        fi
    fi

    echo "Using $PYTHON_CMD for virtual environment"
    "$PYTHON_CMD" -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -e ".[dev]"
    echo "✓ Virtual environment created and dependencies installed"
else
    echo "Virtual environment already exists at .venv"
fi
