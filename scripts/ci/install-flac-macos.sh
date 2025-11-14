#!/bin/bash
# Install flac on macOS with pinned version (built from source)
# Usage: install-flac-macos.sh <pinned_version>
# Example: install-flac-macos.sh "1.4.3"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/macos-common.sh"

if [ $# -lt 1 ]; then
  echo "ERROR: Pinned version required"
  echo "Usage: $0 <pinned_version>"
  exit 1
fi

PINNED_VERSION="$1"

# Check if flac is already installed
NEED_INSTALL=1
if command -v flac &>/dev/null; then
  INSTALLED_VERSION=$(get_tool_version "flac")
  if check_version_match "flac" "$INSTALLED_VERSION" "$PINNED_VERSION"; then
    echo "flac ${INSTALLED_VERSION} already installed (matches pinned version ${PINNED_VERSION})"
    NEED_INSTALL=0
  else
    echo "Removing existing flac version ${INSTALLED_VERSION} (installing pinned version ${PINNED_VERSION})..."
    remove_homebrew_package "flac" "/usr/local/bin/flac /usr/local/bin/metaflac"
  fi
fi

# Install flac from source if needed
if [ "$NEED_INSTALL" -eq 1 ]; then
  echo "Building flac ${PINNED_VERSION} from source..."

  # Check and install build tools if needed
  check_and_install_build_tools

  BUILD_DIR="/tmp/flac_build_${PINNED_VERSION}"
  rm -rf "$BUILD_DIR"
  mkdir -p "$BUILD_DIR"

  SOURCE_URL="https://github.com/xiph/flac/releases/download/${PINNED_VERSION}/flac-${PINNED_VERSION}.tar.xz"
  SOURCE_FILE="${BUILD_DIR}/flac-${PINNED_VERSION}.tar.xz"

  echo "Downloading flac ${PINNED_VERSION} source..."
  curl -L -f -o "$SOURCE_FILE" "$SOURCE_URL" || {
    echo "ERROR: Failed to download flac ${PINNED_VERSION} source."
    echo "URL: ${SOURCE_URL}"
    rm -rf "$BUILD_DIR"
    exit 1
  }

  echo "Extracting and building flac..."
  cd "$BUILD_DIR"
  tar -xf "$SOURCE_FILE" || {
    echo "ERROR: Failed to extract flac source."
    rm -rf "$BUILD_DIR"
    exit 1
  }

  cd "flac-${PINNED_VERSION}"
  ./configure --prefix=/usr/local || {
    echo "ERROR: Failed to configure flac build."
    rm -rf "$BUILD_DIR"
    exit 1
  }

  make -j$(sysctl -n hw.ncpu) || {
    echo "ERROR: Failed to build flac."
    rm -rf "$BUILD_DIR"
    exit 1
  }

  sudo make install || {
    echo "ERROR: Failed to install flac."
    rm -rf "$BUILD_DIR"
    exit 1
  }

  cd /
  rm -rf "$BUILD_DIR"

  echo "flac ${PINNED_VERSION} installed successfully"
fi

