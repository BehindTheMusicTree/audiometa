#!/bin/bash
# Install mediainfo on macOS with pinned version from MediaArea
# Usage: install-mediainfo-macos.sh <pinned_version>
# Example: install-mediainfo-macos.sh "24.12"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/macos-common.sh"

if [ $# -lt 1 ]; then
  echo "ERROR: Pinned version required"
  echo "Usage: $0 <pinned_version>"
  exit 1
fi

PINNED_VERSION="$1"

# Check if mediainfo is already installed
NEED_INSTALL=1
if command -v mediainfo &>/dev/null; then
  INSTALLED_VERSION=$(get_tool_version "mediainfo")
  if check_version_match "mediainfo" "$INSTALLED_VERSION" "$PINNED_VERSION"; then
    echo "mediainfo ${INSTALLED_VERSION} already installed (matches pinned version ${PINNED_VERSION})"
    NEED_INSTALL=0
  else
    echo "Removing existing mediainfo version ${INSTALLED_VERSION} (installing pinned version ${PINNED_VERSION})..."
    remove_homebrew_package "media-info" "/usr/local/bin/mediainfo"
  fi
fi

# Install mediainfo from MediaArea if needed
if [ "$NEED_INSTALL" -eq 1 ]; then
  URL="https://mediaarea.net/download/binary/mediainfo/${PINNED_VERSION}/MediaInfo_CLI_${PINNED_VERSION}_Mac.dmg"
  DMG_FILE="/tmp/mediainfo_${PINNED_VERSION}.dmg"

  echo "Downloading mediainfo version ${PINNED_VERSION} from MediaArea..."
  curl -L -f -o "$DMG_FILE" "$URL" || {
    echo "ERROR: Failed to download mediainfo ${PINNED_VERSION} from MediaArea."
    echo "URL: ${URL}"
    echo "Check available versions at: https://mediaarea.net/en/MediaInfo/Download/Mac"
    exit 1
  }

  echo "Installing mediainfo..."
  if [ ! -f "$DMG_FILE" ] || [ ! -s "$DMG_FILE" ]; then
    echo "ERROR: DMG file is missing or empty."
    rm -f "$DMG_FILE"
    exit 1
  fi

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

  # Check for .pkg file first (newer MediaArea releases)
  PKG_FILE=$(find "$MOUNT_POINT" -name "*.pkg" -type f | head -1)

  if [ -n "$PKG_FILE" ]; then
    # Install the .pkg file (non-interactive mode)
    echo "Installing mediainfo from .pkg installer..."
    sudo installer -pkg "$PKG_FILE" -target / -allowUntrusted || {
      echo "ERROR: Failed to install mediainfo from .pkg file."
      hdiutil detach "$MOUNT_POINT" -quiet || true
      rm -f "$DMG_FILE"
      exit 1
    }

    # After installing .pkg, the executable should be in /usr/local/bin or /opt/local/bin
    # Check common installation locations
    if [ -f "/usr/local/bin/mediainfo" ]; then
      EXE_PATH="/usr/local/bin/mediainfo"
    elif [ -f "/opt/local/bin/mediainfo" ]; then
      # Copy to /usr/local/bin for consistency
      sudo cp "/opt/local/bin/mediainfo" /usr/local/bin/mediainfo
      EXE_PATH="/usr/local/bin/mediainfo"
    else
      # Try to find where installer placed it
      EXE_PATH=$(find /usr/local /opt/local -name "mediainfo" -type f 2>/dev/null | head -1)
      if [ -n "$EXE_PATH" ] && [ "$EXE_PATH" != "/usr/local/bin/mediainfo" ]; then
        sudo cp "$EXE_PATH" /usr/local/bin/mediainfo
        EXE_PATH="/usr/local/bin/mediainfo"
      fi
    fi

    if [ -z "$EXE_PATH" ] || [ ! -f "$EXE_PATH" ]; then
      echo "ERROR: mediainfo executable not found after .pkg installation."
      echo "Searched in /usr/local/bin and /opt/local/bin"
      hdiutil detach "$MOUNT_POINT" -quiet || true
      rm -f "$DMG_FILE"
      exit 1
    fi
  else
    # Fallback: MediaArea DMG structure with .app bundle (older releases)
    EXE_PATH="${MOUNT_POINT}/MediaInfo.app/Contents/MacOS/mediainfo"

    if [ ! -f "$EXE_PATH" ]; then
      echo "ERROR: mediainfo executable not found at expected location: $EXE_PATH"
      echo "Contents of mounted DMG:"
      ls -la "$MOUNT_POINT"
      hdiutil detach "$MOUNT_POINT" -quiet || true
      rm -f "$DMG_FILE"
      exit 1
    fi

    sudo cp "$EXE_PATH" /usr/local/bin/mediainfo || {
      echo "ERROR: Failed to copy mediainfo executable."
      hdiutil detach "$MOUNT_POINT" -quiet || true
      rm -f "$DMG_FILE"
      exit 1
    }

    sudo chmod +x /usr/local/bin/mediainfo
  fi

  hdiutil detach "$MOUNT_POINT" -quiet || true
  rm -f "$DMG_FILE"

  # Ensure /usr/local/bin is in PATH (may not be in CI environments)
  if [ -d "/usr/local/bin" ]; then
    case ":$PATH:" in
      *:/usr/local/bin:*)
        ;;
      *)
        export PATH="/usr/local/bin:$PATH"
        if [ -n "$GITHUB_PATH" ]; then
          echo "/usr/local/bin" >> "$GITHUB_PATH"
        fi
        ;;
    esac
  fi

  echo "mediainfo ${PINNED_VERSION} installed successfully"
fi

