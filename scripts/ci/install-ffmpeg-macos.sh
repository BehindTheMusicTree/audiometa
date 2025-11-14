#!/bin/bash
# Install ffmpeg on macOS with pinned version
# Usage: install-ffmpeg-macos.sh <pinned_version>
# Example: install-ffmpeg-macos.sh "7"

set -e

if [ $# -lt 1 ]; then
  echo "ERROR: Pinned version required"
  echo "Usage: $0 <pinned_version>"
  exit 1
fi

PINNED_VERSION="$1"

# Check if ffmpeg is already installed and remove if version doesn't match
NEED_INSTALL=1
if command -v ffmpeg &>/dev/null; then
  INSTALLED_VERSION=$(ffmpeg -version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")

  if [ -n "$INSTALLED_VERSION" ]; then
    # Extract major version for comparison (e.g., "7.1.2" -> "7")
    INSTALLED_MAJOR=$(echo "$INSTALLED_VERSION" | cut -d. -f1)
    PINNED_MAJOR=$(echo "$PINNED_VERSION" | cut -d. -f1)

    if [ "$INSTALLED_MAJOR" = "$PINNED_MAJOR" ]; then
      echo "ffmpeg ${INSTALLED_VERSION} already installed (matches pinned version ${PINNED_VERSION})"
      NEED_INSTALL=0
      # ffmpeg@7 is keg-only, ensure it's in PATH
      FFMPEG_BIN_PATH="/usr/local/opt/ffmpeg@${PINNED_VERSION}/bin"
      if [ -d "$FFMPEG_BIN_PATH" ]; then
        export PATH="$FFMPEG_BIN_PATH:$PATH"
        if [ -n "$GITHUB_PATH" ]; then
          echo "$FFMPEG_BIN_PATH" >> "$GITHUB_PATH"
        fi
      fi
    else
      echo "Removing existing ffmpeg version ${INSTALLED_VERSION} (installing pinned version ${PINNED_VERSION})..."
      brew uninstall ffmpeg 2>/dev/null || brew uninstall ffmpeg@${INSTALLED_MAJOR} 2>/dev/null || true
    fi
  else
    echo "ffmpeg installed but version could not be determined, removing..."
    brew uninstall ffmpeg 2>/dev/null || true
  fi
fi

# Install ffmpeg with version pinning if needed
if [ "$NEED_INSTALL" -eq 1 ]; then
  echo "Installing ffmpeg@${PINNED_VERSION}..."
  brew install ffmpeg@${PINNED_VERSION} || {
    echo "ERROR: Pinned ffmpeg version ${PINNED_VERSION} not available."
    echo "Check available versions with: brew search ffmpeg"
    exit 1
  }
  # ffmpeg@7 is keg-only, so we need to add it to PATH
  FFMPEG_BIN_PATH="/usr/local/opt/ffmpeg@${PINNED_VERSION}/bin"
  if [ -d "$FFMPEG_BIN_PATH" ]; then
    export PATH="$FFMPEG_BIN_PATH:$PATH"
    # Also add to PATH for verification step
    if [ -n "$GITHUB_PATH" ]; then
      echo "$FFMPEG_BIN_PATH" >> "$GITHUB_PATH"
    fi
  fi
fi

echo "ffmpeg ${PINNED_VERSION} installed successfully"

