#!/bin/bash
# Setup pre-commit hooks with proper environment
# This ensures pre-commit uses the tool versions from pyproject.toml

set -e

echo "Setting up pre-commit environment..."

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected."
    echo "   It's recommended to activate a virtual environment first."
    echo "   Example: python3 -m venv .venv && source .venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install the package with dev dependencies
echo "Installing package with dev dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

echo "✓ Pre-commit setup complete!"
echo ""
echo "Verifying installed tool versions..."
bash .pre-commit-hooks/check-tool-versions.sh
