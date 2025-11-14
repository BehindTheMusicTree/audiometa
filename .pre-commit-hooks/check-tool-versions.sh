#!/bin/bash
# Check that installed tool versions match pyproject.toml
# This ensures pre-commit uses the same versions as CI

set -e

# If .venv exists and VIRTUAL_ENV is not set, add .venv/bin to PATH first
# This handles VS Code Source Control commits where the shell isn't activated
if [ -z "$VIRTUAL_ENV" ] && [ -d ".venv/bin" ] && [ -x ".venv/bin/python" ]; then
    export PATH=".venv/bin:$PATH"
    USING_LOCAL_VENV=true
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Extract version from pyproject.toml
get_expected_version() {
    local tool=$1
    # Match patterns like: "ruff==0.6.9", "isort==5.13.2", etc.
    grep -E "\"${tool}==" pyproject.toml | sed -E "s/.*${tool}==([0-9.]+).*/\1/" | head -1
}

# Get installed version
get_installed_version() {
    local tool=$1
    case $tool in
        ruff)
            ruff --version 2>/dev/null | awk '{print $2}' || echo "NOT_INSTALLED"
            ;;
        isort)
            isort --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "NOT_INSTALLED"
            ;;
        mypy)
            mypy --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "NOT_INSTALLED"
            ;;
        docformatter)
            docformatter --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "NOT_INSTALLED"
            ;;
    esac
}

# Check if we're in a virtual environment (skip check in CI)
check_venv() {
    # Skip venv check in CI environments
    if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
        return 0
    fi

    # Check if we're using local .venv (set at top of script)
    if [ "$USING_LOCAL_VENV" = "true" ]; then
        echo -e "${YELLOW}Note: Using tools from .venv (virtual environment not activated in shell)${NC}"
        return 0
    fi

    # Check if VIRTUAL_ENV is set
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${RED}ERROR: No virtual environment detected!${NC}"
        echo -e "${YELLOW}Pre-commit hooks require tools from .venv${NC}"
        echo ""
        echo "Please activate your virtual environment:"
        echo "  source .venv/bin/activate  # Linux/macOS"
        echo "  .venv\\Scripts\\activate   # Windows"
        echo ""
        echo "Or run the setup script:"
        echo "  ./scripts/setup-precommit.sh"
        return 1
    fi
    return 0
}

# Main validation
main() {
    echo "Checking tool versions..."

    # Check virtual environment first (unless in CI)
    if ! check_venv; then
        exit 1
    fi

    local has_errors=0
    local tools=("ruff" "isort" "mypy" "docformatter")

    for tool in "${tools[@]}"; do
        expected=$(get_expected_version "$tool")
        installed=$(get_installed_version "$tool")

        if [ "$installed" = "NOT_INSTALLED" ]; then
            echo -e "${RED}✗ $tool: NOT INSTALLED${NC}"
            has_errors=1
        elif [ "$installed" != "$expected" ]; then
            echo -e "${RED}✗ $tool: version mismatch${NC}"
            echo -e "  Expected: ${YELLOW}$expected${NC} (from pyproject.toml)"
            echo -e "  Installed: ${YELLOW}$installed${NC}"
            has_errors=1
        else
            echo -e "${GREEN}✓ $tool: $installed${NC}"
        fi
    done

    if [ $has_errors -eq 1 ]; then
        echo ""
        echo -e "${RED}ERROR: Tool version mismatch detected!${NC}"
        echo ""
        echo "To fix this:"
        echo "  1. Activate your virtual environment (if not already active)"
        echo "  2. Reinstall dev dependencies: pip install -e \".[dev]\""
        echo "  3. Or run the setup script: ./scripts/setup-precommit.sh"
        echo ""
        echo "This ensures pre-commit uses the same tool versions as CI."
        exit 1
    fi

    echo -e "${GREEN}All tool versions match pyproject.toml ✓${NC}"
    exit 0
}

main
