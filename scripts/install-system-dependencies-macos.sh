#!/bin/bash
# Install system dependencies for macOS CI
# Pinned versions from system-dependencies.toml (fails if not available, no fallback)
# See system-dependencies.toml for version configuration

set -e

# Load pinned versions from system-dependencies.toml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION_OUTPUT=$(python3 "${SCRIPT_DIR}/ci/load-system-dependency-versions.py" bash)
if [ $? -ne 0 ] || [ -z "$VERSION_OUTPUT" ]; then
  echo "ERROR: Failed to load versions from system-dependencies.toml"
  exit 1
fi
eval "$VERSION_OUTPUT"

# Verify versions were loaded
if [ -z "$PINNED_FFMPEG" ] || [ -z "$PINNED_FLAC" ] || [ -z "$PINNED_MEDIAINFO" ] || [ -z "$PINNED_ID3V2" ] || [ -z "$PINNED_BWFMETAEDIT" ]; then
  echo "ERROR: Failed to load all required versions from system-dependencies.toml"
  echo "Loaded versions:"
  echo "  PINNED_FFMPEG=${PINNED_FFMPEG:-NOT SET}"
  echo "  PINNED_FLAC=${PINNED_FLAC:-NOT SET}"
  echo "  PINNED_MEDIAINFO=${PINNED_MEDIAINFO:-NOT SET}"
  echo "  PINNED_ID3V2=${PINNED_ID3V2:-NOT SET}"
  echo "  PINNED_BWFMETAEDIT=${PINNED_BWFMETAEDIT:-NOT SET}"
  exit 1
fi

echo "Installing pinned package versions..."

# Homebrew version pinning: Only ffmpeg supports @version syntax
# Other packages (flac, mediainfo/media-info, id3v2, bwfmetaedit) don't support version pinning

# Check if ffmpeg is already installed and remove if version doesn't match
NEED_INSTALL_FFMPEG=1
if command -v ffmpeg &>/dev/null; then
  INSTALLED_FFMPEG_VERSION=$(ffmpeg -version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")

  if [ -n "$INSTALLED_FFMPEG_VERSION" ]; then
    # Extract major version for comparison (e.g., "7.1.2" -> "7")
    INSTALLED_MAJOR=$(echo "$INSTALLED_FFMPEG_VERSION" | cut -d. -f1)
    PINNED_MAJOR=$(echo "$PINNED_FFMPEG" | cut -d. -f1)

    if [ "$INSTALLED_MAJOR" = "$PINNED_MAJOR" ]; then
      echo "ffmpeg ${INSTALLED_FFMPEG_VERSION} already installed (matches pinned version ${PINNED_FFMPEG})"
      NEED_INSTALL_FFMPEG=0
      # ffmpeg@7 is keg-only, ensure it's in PATH
      FFMPEG_BIN_PATH="/usr/local/opt/ffmpeg@${PINNED_FFMPEG}/bin"
      if [ -d "$FFMPEG_BIN_PATH" ]; then
        export PATH="$FFMPEG_BIN_PATH:$PATH"
        if [ -n "$GITHUB_PATH" ]; then
          echo "$FFMPEG_BIN_PATH" >> "$GITHUB_PATH"
        fi
      fi
    else
      echo "Removing existing ffmpeg version ${INSTALLED_FFMPEG_VERSION} (installing pinned version ${PINNED_FFMPEG})..."
      brew uninstall ffmpeg 2>/dev/null || brew uninstall ffmpeg@${INSTALLED_MAJOR} 2>/dev/null || true
    fi
  else
    echo "ffmpeg installed but version could not be determined, removing..."
    brew uninstall ffmpeg 2>/dev/null || true
  fi
fi

# Install ffmpeg with version pinning if needed
if [ "$NEED_INSTALL_FFMPEG" -eq 1 ]; then
  echo "Installing ffmpeg@${PINNED_FFMPEG}..."
  brew install ffmpeg@${PINNED_FFMPEG} || {
    echo "ERROR: Pinned ffmpeg version ${PINNED_FFMPEG} not available."
    echo "Check available versions with: brew search ffmpeg"
    exit 1
  }
  # ffmpeg@7 is keg-only, so we need to add it to PATH
  FFMPEG_BIN_PATH="/usr/local/opt/ffmpeg@${PINNED_FFMPEG}/bin"
  if [ -d "$FFMPEG_BIN_PATH" ]; then
    export PATH="$FFMPEG_BIN_PATH:$PATH"
    # Also add to PATH for verification step
    if [ -n "$GITHUB_PATH" ]; then
      echo "$FFMPEG_BIN_PATH" >> "$GITHUB_PATH"
    fi
  fi
fi

# Install packages without @version syntax (Homebrew doesn't support @version for these)
# Note: mediainfo is called media-info in Homebrew
# Check installed versions and remove/reinstall if major.minor doesn't match pinned version
PACKAGES_TO_INSTALL=()

# Check flac
NEED_INSTALL_FLAC=1
if command -v flac &>/dev/null; then
  INSTALLED_FLAC_VERSION=$(flac --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
  if [ -n "$INSTALLED_FLAC_VERSION" ]; then
    INSTALLED_MAJOR_MINOR=$(echo "$INSTALLED_FLAC_VERSION" | cut -d. -f1,2)
    PINNED_MAJOR_MINOR=$(echo "$PINNED_FLAC" | cut -d. -f1,2)
    if [ "$INSTALLED_MAJOR_MINOR" = "$PINNED_MAJOR_MINOR" ]; then
      echo "flac ${INSTALLED_FLAC_VERSION} already installed (matches pinned version ${PINNED_FLAC})"
      NEED_INSTALL_FLAC=0
    else
      echo "Removing existing flac version ${INSTALLED_FLAC_VERSION} (installing pinned version ${PINNED_FLAC})..."
      brew uninstall flac 2>/dev/null || true
    fi
  fi
fi
if [ "$NEED_INSTALL_FLAC" -eq 1 ]; then
  PACKAGES_TO_INSTALL+=("flac")
fi

# Check media-info (mediainfo)
NEED_INSTALL_MEDIAINFO=1
if command -v mediainfo &>/dev/null; then
  INSTALLED_MEDIAINFO_VERSION=$(mediainfo --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
  if [ -n "$INSTALLED_MEDIAINFO_VERSION" ]; then
    INSTALLED_MAJOR_MINOR=$(echo "$INSTALLED_MEDIAINFO_VERSION" | cut -d. -f1,2)
    PINNED_MAJOR_MINOR=$(echo "$PINNED_MEDIAINFO" | cut -d. -f1,2)
    if [ "$INSTALLED_MAJOR_MINOR" = "$PINNED_MAJOR_MINOR" ]; then
      echo "mediainfo ${INSTALLED_MEDIAINFO_VERSION} already installed (matches pinned version ${PINNED_MEDIAINFO})"
      NEED_INSTALL_MEDIAINFO=0
    else
      echo "Removing existing mediainfo version ${INSTALLED_MEDIAINFO_VERSION} (installing pinned version ${PINNED_MEDIAINFO})..."
      brew uninstall media-info 2>/dev/null || true
    fi
  fi
fi
if [ "$NEED_INSTALL_MEDIAINFO" -eq 1 ]; then
  PACKAGES_TO_INSTALL+=("media-info")
fi

# Check id3v2
NEED_INSTALL_ID3V2=1
if command -v id3v2 &>/dev/null; then
  INSTALLED_ID3V2_VERSION=$(id3v2 --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
  if [ -n "$INSTALLED_ID3V2_VERSION" ]; then
    INSTALLED_MAJOR_MINOR=$(echo "$INSTALLED_ID3V2_VERSION" | cut -d. -f1,2)
    PINNED_MAJOR_MINOR=$(echo "$PINNED_ID3V2" | cut -d. -f1,2)
    if [ "$INSTALLED_MAJOR_MINOR" = "$PINNED_MAJOR_MINOR" ]; then
      echo "id3v2 ${INSTALLED_ID3V2_VERSION} already installed (matches pinned version ${PINNED_ID3V2})"
      NEED_INSTALL_ID3V2=0
    else
      echo "Removing existing id3v2 version ${INSTALLED_ID3V2_VERSION} (installing pinned version ${PINNED_ID3V2})..."
      brew uninstall id3v2 2>/dev/null || true
    fi
  fi
fi
if [ "$NEED_INSTALL_ID3V2" -eq 1 ]; then
  PACKAGES_TO_INSTALL+=("id3v2")
fi

# Verify Homebrew versions match pinned versions before installing
if [ ${#PACKAGES_TO_INSTALL[@]} -gt 0 ]; then
  echo "Checking Homebrew versions match pinned versions..."
  VERSION_MISMATCH=0

  for package in "${PACKAGES_TO_INSTALL[@]}"; do
    case "$package" in
      flac)
        BREW_VERSION=$(brew info flac 2>/dev/null | grep -E "^==>.*stable" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || echo "")
        PINNED_MAJOR_MINOR=$(echo "$PINNED_FLAC" | cut -d. -f1,2)
        if [ -n "$BREW_VERSION" ]; then
          BREW_MAJOR_MINOR=$(echo "$BREW_VERSION" | cut -d. -f1,2)
          if [ "$BREW_MAJOR_MINOR" != "$PINNED_MAJOR_MINOR" ]; then
            echo "ERROR: Homebrew flac version ${BREW_VERSION} (major.minor: ${BREW_MAJOR_MINOR}) doesn't match pinned version ${PINNED_FLAC} (major.minor: ${PINNED_MAJOR_MINOR})"
            VERSION_MISMATCH=1
          else
            echo "✓ Homebrew flac version ${BREW_VERSION} matches pinned version ${PINNED_FLAC}"
          fi
        fi
        ;;
      media-info)
        BREW_VERSION=$(brew info media-info 2>/dev/null | grep -E "^==>.*stable" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || echo "")
        PINNED_MAJOR_MINOR=$(echo "$PINNED_MEDIAINFO" | cut -d. -f1,2)
        if [ -n "$BREW_VERSION" ]; then
          BREW_MAJOR_MINOR=$(echo "$BREW_VERSION" | cut -d. -f1,2)
          if [ "$BREW_MAJOR_MINOR" != "$PINNED_MAJOR_MINOR" ]; then
            echo "ERROR: Homebrew media-info version ${BREW_VERSION} (major.minor: ${BREW_MAJOR_MINOR}) doesn't match pinned version ${PINNED_MEDIAINFO} (major.minor: ${PINNED_MAJOR_MINOR})"
            VERSION_MISMATCH=1
          else
            echo "✓ Homebrew media-info version ${BREW_VERSION} matches pinned version ${PINNED_MEDIAINFO}"
          fi
        fi
        ;;
      id3v2)
        BREW_VERSION=$(brew info id3v2 2>/dev/null | grep -E "^==>.*stable" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || echo "")
        PINNED_MAJOR_MINOR=$(echo "$PINNED_ID3V2" | cut -d. -f1,2)
        if [ -n "$BREW_VERSION" ]; then
          BREW_MAJOR_MINOR=$(echo "$BREW_VERSION" | cut -d. -f1,2)
          if [ "$BREW_MAJOR_MINOR" != "$PINNED_MAJOR_MINOR" ]; then
            echo "ERROR: Homebrew id3v2 version ${BREW_VERSION} (major.minor: ${BREW_MAJOR_MINOR}) doesn't match pinned version ${PINNED_ID3V2} (major.minor: ${PINNED_MAJOR_MINOR})"
            VERSION_MISMATCH=1
          else
            echo "✓ Homebrew id3v2 version ${BREW_VERSION} matches pinned version ${PINNED_ID3V2}"
          fi
        fi
        ;;
    esac
  done

  if [ "$VERSION_MISMATCH" -eq 1 ]; then
    echo ""
    echo "ERROR: Cannot install packages - Homebrew versions don't match pinned versions."
    echo "Homebrew doesn't support @version syntax for these packages, so we cannot install exact versions."
    echo "Consider installing from source or downloading binaries to ensure version pinning."
    exit 1
  fi

  echo "Installing ${PACKAGES_TO_INSTALL[*]}..."
  brew install "${PACKAGES_TO_INSTALL[@]}" || {
    echo "ERROR: Failed to install packages."
    echo "Check available packages with: brew search <package>"
    exit 1
  }
fi

# Check if bwfmetaedit is already installed and remove if version doesn't match
NEED_INSTALL_BWFMETAEDIT=1
if command -v bwfmetaedit &>/dev/null; then
  INSTALLED_BWFMETAEDIT_VERSION=$(bwfmetaedit --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")

  if [ -n "$INSTALLED_BWFMETAEDIT_VERSION" ]; then
    INSTALLED_MAJOR_MINOR=$(echo "$INSTALLED_BWFMETAEDIT_VERSION" | cut -d. -f1,2)
    PINNED_MAJOR_MINOR=$(echo "$PINNED_BWFMETAEDIT" | cut -d. -f1,2)

    if [ "$INSTALLED_MAJOR_MINOR" = "$PINNED_MAJOR_MINOR" ]; then
      echo "bwfmetaedit ${INSTALLED_BWFMETAEDIT_VERSION} already installed (matches pinned version ${PINNED_BWFMETAEDIT})"
      NEED_INSTALL_BWFMETAEDIT=0
    else
      echo "Removing existing bwfmetaedit version ${INSTALLED_BWFMETAEDIT_VERSION} (installing pinned version ${PINNED_BWFMETAEDIT})..."
      # Remove if installed via Homebrew
      brew uninstall bwfmetaedit 2>/dev/null || true
      # Remove if installed manually (from MediaArea)
      if [ -f "/usr/local/bin/bwfmetaedit" ]; then
        sudo rm -f /usr/local/bin/bwfmetaedit
      fi
    fi
  else
    echo "bwfmetaedit installed but version could not be determined, removing..."
    brew uninstall bwfmetaedit 2>/dev/null || true
    if [ -f "/usr/local/bin/bwfmetaedit" ]; then
      sudo rm -f /usr/local/bin/bwfmetaedit
    fi
  fi
fi

# Install bwfmetaedit from MediaArea if needed (pinned version)
if [ "$NEED_INSTALL_BWFMETAEDIT" -eq 1 ]; then
  PINNED_VERSION="${PINNED_BWFMETAEDIT}"
  URL="https://mediaarea.net/download/binary/bwfmetaedit/${PINNED_VERSION}/BWFMetaEdit_CLI_${PINNED_VERSION}_Mac.dmg"
  DMG_FILE="/tmp/bwfmetaedit_${PINNED_VERSION}.dmg"

  echo "Downloading bwfmetaedit version ${PINNED_VERSION} from MediaArea..."
  curl -L -o "$DMG_FILE" "$URL" || {
    echo "ERROR: Failed to download bwfmetaedit ${PINNED_VERSION} from MediaArea."
    echo "URL: ${URL}"
    exit 1
  }

  echo "Installing bwfmetaedit..."
  # Verify DMG file exists and has content
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

  echo "bwfmetaedit ${PINNED_VERSION} installed successfully"
fi

# Verify installed versions (informational only for packages without version pinning)
echo "Verifying installed versions..."
INSTALLED_FLAC=$(brew list --versions flac | awk '{print $2}')
INSTALLED_MEDIAINFO=$(brew list --versions media-info | awk '{print $2}')
INSTALLED_ID3V2=$(brew list --versions id3v2 | awk '{print $2}')
INSTALLED_BWFMETAEDIT=$(bwfmetaedit --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "not found")

echo "  flac: ${INSTALLED_FLAC:-not found} (expected: ${PINNED_FLAC})"
echo "  media-info: ${INSTALLED_MEDIAINFO:-not found} (expected: ${PINNED_MEDIAINFO})"
echo "  id3v2: ${INSTALLED_ID3V2:-not found} (expected: ${PINNED_ID3V2})"
echo "  bwfmetaedit: ${INSTALLED_BWFMETAEDIT:-not found} (expected: ${PINNED_BWFMETAEDIT})"

# Note: Homebrew doesn't support @version syntax for flac, mediainfo, id3v2, bwfmetaedit
# The script checks installed versions and removes/reinstalls if major.minor doesn't match,
# but cannot guarantee exact version matching since Homebrew installs the latest available version.
# bwfmetaedit is downloaded from MediaArea with exact version pinning.

echo "Verifying installed tools are available in PATH..."
MISSING_TOOLS=()

# Check each tool, including ffprobe which comes from ffmpeg@7 (keg-only)
for tool in ffprobe flac metaflac mediainfo id3v2; do
  if ! command -v "$tool" &>/dev/null; then
    MISSING_TOOLS+=("$tool")
  fi
done

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
  echo "ERROR: The following tools are not available in PATH after installation:"
  printf '  - %s\n' "${MISSING_TOOLS[@]}"
  echo ""
  echo "Installation may have failed. Check the output above for errors."
  echo ""
  echo "Note: On macOS, you may need to add Homebrew's bin directory to PATH:"
  echo "  export PATH=\"/opt/homebrew/bin:\$PATH\"  # Apple Silicon"
  echo "  export PATH=\"/usr/local/bin:\$PATH\"     # Intel"
  echo ""
  echo "Note: ffmpeg@7 is keg-only. If ffprobe is missing, ensure PATH includes:"
  echo "  export PATH=\"/usr/local/opt/ffmpeg@7/bin:\$PATH\""
  exit 1
fi

echo "All system dependencies installed successfully!"

