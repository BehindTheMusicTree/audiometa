#!/bin/bash
# Install id3v2 on macOS with pinned version (built from source)
# Usage: install-id3v2-macos.sh <pinned_version>
# Example: install-id3v2-macos.sh "0.1.12"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/macos-common.sh"

if [ $# -lt 1 ]; then
  echo "ERROR: Pinned version required"
  echo "Usage: $0 <pinned_version>"
  exit 1
fi

PINNED_VERSION="$1"

# Check if id3v2 is already installed
NEED_INSTALL=1
if command -v id3v2 &>/dev/null; then
  INSTALLED_VERSION=$(get_tool_version "id3v2")
  if check_version_match "id3v2" "$INSTALLED_VERSION" "$PINNED_VERSION"; then
    echo "id3v2 ${INSTALLED_VERSION} already installed (matches pinned version ${PINNED_VERSION})"
    NEED_INSTALL=0
  else
    echo "Removing existing id3v2 version ${INSTALLED_VERSION} (installing pinned version ${PINNED_VERSION})..."
    remove_homebrew_package "id3v2" "/usr/local/bin/id3v2"
  fi
fi

# Install id3v2 from source if needed
if [ "$NEED_INSTALL" -eq 1 ]; then
  echo "Building id3v2 ${PINNED_VERSION} from source..."

  # Check and install build tools if needed
  check_and_install_build_tools

  # id3v2 requires id3lib - check if available via Homebrew (as dependency)
  if ! command -v id3lib-config &>/dev/null; then
    echo "Installing id3lib dependency via Homebrew..."
    brew install id3lib || {
      echo "ERROR: Failed to install id3lib dependency."
      exit 1
    }
  fi

  BUILD_DIR="/tmp/id3v2_build_${PINNED_VERSION}"
  rm -rf "$BUILD_DIR"
  mkdir -p "$BUILD_DIR"

  SOURCE_URL="https://sourceforge.net/projects/id3v2/files/id3v2/${PINNED_VERSION}/id3v2-${PINNED_VERSION}.tar.gz/download"
  SOURCE_FILE="${BUILD_DIR}/id3v2-${PINNED_VERSION}.tar.gz"

  echo "Downloading id3v2 ${PINNED_VERSION} source..."
  curl -L -f -o "$SOURCE_FILE" "$SOURCE_URL" || {
    echo "ERROR: Failed to download id3v2 ${PINNED_VERSION} source."
    echo "URL: ${SOURCE_URL}"
    rm -rf "$BUILD_DIR"
    exit 1
  }

  echo "Extracting and building id3v2..."
  cd "$BUILD_DIR"
  tar -xzf "$SOURCE_FILE" || {
    echo "ERROR: Failed to extract id3v2 source."
    rm -rf "$BUILD_DIR"
    exit 1
  }

  cd "id3v2-${PINNED_VERSION}"
  make || {
    echo "ERROR: Failed to build id3v2."
    rm -rf "$BUILD_DIR"
    exit 1
  }

  sudo cp id3v2 /usr/local/bin/id3v2 || {
    echo "ERROR: Failed to install id3v2."
    rm -rf "$BUILD_DIR"
    exit 1
  }

  sudo chmod +x /usr/local/bin/id3v2

  # Ensure /usr/local/bin is in PATH (may not be in CI environments)
  if [ -d "/usr/local/bin" ] && [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
    export PATH="/usr/local/bin:$PATH"
    if [ -n "$GITHUB_PATH" ]; then
      echo "/usr/local/bin" >> "$GITHUB_PATH"
    fi
  fi

  cd /
  rm -rf "$BUILD_DIR"

  echo "id3v2 ${PINNED_VERSION} installed successfully"
fi

