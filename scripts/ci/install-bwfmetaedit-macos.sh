#!/bin/bash
# Install bwfmetaedit on macOS with pinned version from MediaArea
# Usage: install-bwfmetaedit-macos.sh <pinned_version>
# Example: install-bwfmetaedit-macos.sh "25.04.1"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/macos-common.sh"

if [ $# -lt 1 ]; then
  echo "ERROR: Pinned version required"
  echo "Usage: $0 <pinned_version>"
  exit 1
fi

PINNED_VERSION="$1"

# Check if bwfmetaedit is already installed
NEED_INSTALL=1
if command -v bwfmetaedit &>/dev/null; then
  INSTALLED_VERSION=$(get_tool_version "bwfmetaedit")
  if check_version_match "bwfmetaedit" "$INSTALLED_VERSION" "$PINNED_VERSION"; then
    echo "bwfmetaedit ${INSTALLED_VERSION} already installed (matches pinned version ${PINNED_VERSION})"
    NEED_INSTALL=0
  else
    echo "Removing existing bwfmetaedit version ${INSTALLED_VERSION} (installing pinned version ${PINNED_VERSION})..."
    # Remove if installed via Homebrew
    brew uninstall bwfmetaedit 2>/dev/null || true
    # Remove if installed manually (from MediaArea)
    if [ -f "/usr/local/bin/bwfmetaedit" ]; then
      sudo rm -f /usr/local/bin/bwfmetaedit
    fi
  fi
else
  # Also check if installed but version could not be determined
  if command -v bwfmetaedit &>/dev/null; then
    echo "bwfmetaedit installed but version could not be determined, removing..."
    brew uninstall bwfmetaedit 2>/dev/null || true
    if [ -f "/usr/local/bin/bwfmetaedit" ]; then
      sudo rm -f /usr/local/bin/bwfmetaedit
    fi
  fi
fi

# Install bwfmetaedit from MediaArea if needed
if [ "$NEED_INSTALL" -eq 1 ]; then
  URL="https://mediaarea.net/download/binary/bwfmetaedit/${PINNED_VERSION}/BWFMetaEdit_CLI_${PINNED_VERSION}_Mac.dmg"
  DMG_FILE="/tmp/bwfmetaedit_${PINNED_VERSION}.dmg"

  echo "Downloading bwfmetaedit version ${PINNED_VERSION} from MediaArea..."
  curl -L -o "$DMG_FILE" "$URL" || {
    echo "ERROR: Failed to download bwfmetaedit ${PINNED_VERSION} from MediaArea."
    echo "URL: ${URL}"
    exit 1
  }

  echo "Installing bwfmetaedit..."
  if [ ! -f "$DMG_FILE" ] || [ ! -s "$DMG_FILE" ]; then
    echo "ERROR: DMG file is missing or empty."
    rm -f "$DMG_FILE"
    exit 1
  fi

  # Mount DMG (let macOS determine mount point)
  MOUNT_OUTPUT=$(hdiutil attach "$DMG_FILE" -nobrowse 2>&1)
  MOUNT_EXIT_CODE=$?

  if [ $MOUNT_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Failed to mount DMG file (exit code: $MOUNT_EXIT_CODE)."
    echo "hdiutil output:"
    echo "$MOUNT_OUTPUT"
    rm -f "$DMG_FILE"
    exit 1
  fi

  MOUNT_POINT=$(echo "$MOUNT_OUTPUT" | tail -1 | awk -F'\t' '{print $3}')

  if [ -z "$MOUNT_POINT" ] || [ ! -d "$MOUNT_POINT" ]; then
    echo "ERROR: Failed to determine mount point or mount point is invalid."
    echo "hdiutil output:"
    echo "$MOUNT_OUTPUT"
    rm -f "$DMG_FILE"
    exit 1
  fi

  # Check if DMG contains a .pkg installer (common for macOS DMGs)
  PKG_FILE=$(find "$MOUNT_POINT" -name "*.pkg" -type f | head -1)

  if [ -n "$PKG_FILE" ]; then
    # Install the .pkg file (non-interactive mode)
    echo "Installing bwfmetaedit from .pkg installer..."
    sudo installer -pkg "$PKG_FILE" -target / -allowUntrusted || {
      echo "ERROR: Failed to install bwfmetaedit from .pkg file."
      hdiutil detach "$MOUNT_POINT" -quiet || true
      rm -f "$DMG_FILE"
      exit 1
    }

    # After installing .pkg, the executable should be in /usr/local/bin or /opt/local/bin
    # Check common installation locations
    if [ -f "/usr/local/bin/bwfmetaedit" ]; then
      EXE_PATH="/usr/local/bin/bwfmetaedit"
    elif [ -f "/opt/local/bin/bwfmetaedit" ]; then
      # Copy to /usr/local/bin for consistency
      sudo cp "/opt/local/bin/bwfmetaedit" /usr/local/bin/bwfmetaedit
      EXE_PATH="/usr/local/bin/bwfmetaedit"
    else
      # Try to find where installer placed it
      EXE_PATH=$(find /usr/local /opt/local -name "bwfmetaedit" -type f 2>/dev/null | head -1)
      if [ -n "$EXE_PATH" ] && [ "$EXE_PATH" != "/usr/local/bin/bwfmetaedit" ]; then
        sudo cp "$EXE_PATH" /usr/local/bin/bwfmetaedit
        EXE_PATH="/usr/local/bin/bwfmetaedit"
      fi
    fi

    if [ -z "$EXE_PATH" ] || [ ! -f "$EXE_PATH" ]; then
      echo "ERROR: bwfmetaedit executable not found after .pkg installation."
      echo "Searched in /usr/local/bin and /opt/local/bin"
      hdiutil detach "$MOUNT_POINT" -quiet || true
      rm -f "$DMG_FILE"
      exit 1
    fi
  else
    # MediaArea DMG structure: BWFMetaEdit.app/Contents/MacOS/bwfmetaedit
    EXE_PATH="${MOUNT_POINT}/BWFMetaEdit.app/Contents/MacOS/bwfmetaedit"

    if [ ! -f "$EXE_PATH" ]; then
      echo "ERROR: bwfmetaedit executable not found at expected location: $EXE_PATH"
      echo "Contents of mounted DMG:"
      ls -la "$MOUNT_POINT"
      echo ""
      echo "Looking for .app bundles:"
      find "$MOUNT_POINT" -name "*.app" -type d
      hdiutil detach "$MOUNT_POINT" -quiet || true
      rm -f "$DMG_FILE"
      exit 1
    fi

    # Copy executable to /usr/local/bin
    sudo cp "$EXE_PATH" /usr/local/bin/bwfmetaedit || {
      echo "ERROR: Failed to copy bwfmetaedit executable."
      hdiutil detach "$MOUNT_POINT" -quiet || true
      rm -f "$DMG_FILE"
      exit 1
    }

    sudo chmod +x /usr/local/bin/bwfmetaedit
  fi

  # Unmount and cleanup
  hdiutil detach "$MOUNT_POINT" -quiet || true
  rm -f "$DMG_FILE"

  # Ensure /usr/local/bin is in PATH (may not be in CI environments)
  if [ -d "/usr/local/bin" ] && [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
    export PATH="/usr/local/bin:$PATH"
    if [ -n "$GITHUB_PATH" ]; then
      echo "/usr/local/bin" >> "$GITHUB_PATH"
    fi
  fi

  echo "bwfmetaedit ${PINNED_VERSION} installed successfully"
fi

