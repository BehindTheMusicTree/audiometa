#!/bin/bash

# Script to free up cache space on macOS
# This script safely clears various cache directories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to get directory size
get_size() {
    if [ -d "$1" ]; then
        du -sh "$1" 2>/dev/null | awk '{print $1}'
    else
        echo "0B"
    fi
}

# Function to get directory size in bytes (for calculation)
get_size_bytes() {
    if [ -d "$1" ]; then
        du -sk "$1" 2>/dev/null | awk '{print $1}'
    else
        echo "0"
    fi
}

# Function to clear cache directory
clear_cache() {
    local cache_dir=$1
    local description=$2

    if [ ! -d "$cache_dir" ]; then
        echo -e "${YELLOW}⚠️  $description: Directory not found, skipping${NC}"
        return
    fi

    local size_before=$(get_size_bytes "$cache_dir")
    local size_before_human=$(get_size "$cache_dir")

    echo -e "${YELLOW}Clearing: $description${NC}"
    echo "  Location: $cache_dir"
    echo "  Size before: $size_before_human"

    # Remove contents but keep directory structure
    find "$cache_dir" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true

    local size_after=$(get_size_bytes "$cache_dir")
    local size_freed=$((size_before - size_after))
    local size_freed_mb=$((size_freed / 1024))

    if [ $size_freed_mb -gt 0 ]; then
        echo -e "${GREEN}  ✓ Freed: ${size_freed_mb}MB${NC}"
    else
        echo -e "${GREEN}  ✓ Already clean${NC}"
    fi
    echo ""
}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}macOS Cache Cleanup Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check available space before
echo -e "${YELLOW}Current disk space:${NC}"
df -h / | tail -1
echo ""

# Get initial free space
initial_free=$(df -k / | tail -1 | awk '{print $4}')

# User caches
clear_cache "$HOME/Library/Caches" "User Library Caches"

# Browser caches (optional - uncomment if needed)
# clear_cache "$HOME/Library/Caches/Google/Chrome" "Chrome Cache"
# clear_cache "$HOME/Library/Caches/com.apple.Safari" "Safari Cache"
# clear_cache "$HOME/Library/Caches/com.mozilla.firefox" "Firefox Cache"

# Xcode derived data (if exists)
clear_cache "$HOME/Library/Developer/Xcode/DerivedData" "Xcode Derived Data"

# Xcode archives (if exists)
clear_cache "$HOME/Library/Developer/Xcode/Archives" "Xcode Archives"

# npm cache (if exists)
if command -v npm &> /dev/null; then
    echo -e "${YELLOW}Clearing: npm cache${NC}"
    npm cache clean --force 2>/dev/null || true
    echo -e "${GREEN}  ✓ npm cache cleared${NC}"
    echo ""
fi

# pip cache (if exists)
if command -v pip &> /dev/null; then
    echo -e "${YELLOW}Clearing: pip cache${NC}"
    pip cache purge 2>/dev/null || true
    echo -e "${GREEN}  ✓ pip cache cleared${NC}"
    echo ""
fi

# Homebrew cache (if exists)
if command -v brew &> /dev/null; then
    echo -e "${YELLOW}Clearing: Homebrew cache${NC}"
    brew cleanup --prune=all 2>/dev/null || true
    echo -e "${GREEN}  ✓ Homebrew cache cleared${NC}"
    echo ""
fi

# Docker cache (if Docker is running)
if command -v docker &> /dev/null && docker info &>/dev/null; then
    echo -e "${YELLOW}Clearing: Docker system cache${NC}"
    docker system prune -af --volumes 2>/dev/null || true
    echo -e "${GREEN}  ✓ Docker cache cleared${NC}"
    echo ""
fi

# Cursor IDE caches (if exists)
CURSOR_DIR="$HOME/Library/Application Support/Cursor"
if [ -d "$CURSOR_DIR" ]; then
    # Check if Cursor is running
    if pgrep -f "Cursor" > /dev/null; then
        echo -e "${YELLOW}⚠️  Cursor appears to be running. Cache clearing may be incomplete.${NC}"
        echo -e "${YELLOW}    Consider closing Cursor before running this script for best results.${NC}"
        echo ""
    fi

    echo -e "${YELLOW}Clearing: Cursor IDE caches${NC}"

    # Safe cache directories to clear
    clear_cache "$CURSOR_DIR/CachedData" "Cursor CachedData"
    clear_cache "$CURSOR_DIR/Cache" "Cursor Cache"
    clear_cache "$CURSOR_DIR/CachedExtensionVSIXs" "Cursor Extension Cache"
    clear_cache "$CURSOR_DIR/GPUCache" "Cursor GPU Cache"
    clear_cache "$CURSOR_DIR/Code Cache" "Cursor Code Cache"
    clear_cache "$CURSOR_DIR/WebStorage" "Cursor Web Storage"
    clear_cache "$CURSOR_DIR/logs" "Cursor Logs"

    # Also check ~/Library/Caches for Cursor
    if [ -d "$HOME/Library/Caches/com.todesktop.230313mzl4w4u92" ]; then
        clear_cache "$HOME/Library/Caches/com.todesktop.230313mzl4w4u92" "Cursor System Cache"
    fi

    echo -e "${GREEN}  ✓ Cursor caches cleared${NC}"
    echo ""
fi

# Empty Trash
echo -e "${YELLOW}Emptying Trash...${NC}"
rm -rf ~/.Trash/* 2>/dev/null || true
echo -e "${GREEN}  ✓ Trash emptied${NC}"
echo ""

# Get final free space
final_free=$(df -k / | tail -1 | awk '{print $4}')
space_freed=$((final_free - initial_free))
space_freed_mb=$((space_freed / 1024))
space_freed_gb=$(echo "scale=2; $space_freed / 1048576" | bc)

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Final disk space:${NC}"
df -h / | tail -1
echo ""

if [ $space_freed_mb -gt 0 ]; then
    if [ $space_freed_mb -gt 1024 ]; then
        echo -e "${GREEN}Total space freed: ${space_freed_gb}GB${NC}"
    else
        echo -e "${GREEN}Total space freed: ${space_freed_mb}MB${NC}"
    fi
else
    echo -e "${YELLOW}No significant space was freed (may need admin privileges for system caches)${NC}"
fi
echo ""
