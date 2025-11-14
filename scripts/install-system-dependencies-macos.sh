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
fi

# Install packages without version pinning (Homebrew doesn't support @version for these)
# Note: mediainfo is called media-info in Homebrew
# Check installed versions and remove if different before installing
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

# Install packages if any need installation
if [ ${#PACKAGES_TO_INSTALL[@]} -gt 0 ]; then
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
  # Mount DMG (let macOS determine mount point)
  MOUNT_OUTPUT=$(hdiutil attach "$DMG_FILE" -quiet -nobrowse | tail -1)
  MOUNT_POINT=$(echo "$MOUNT_OUTPUT" | awk -F'\t' '{print $3}')

  if [ -z "$MOUNT_POINT" ]; then
    echo "ERROR: Failed to mount DMG file."
    rm -f "$DMG_FILE"
    exit 1
  fi

  # Find bwfmetaedit executable in the mounted volume
  EXE_PATH=$(find "$MOUNT_POINT" -name "bwfmetaedit" -type f | head -1)

  if [ -z "$EXE_PATH" ]; then
    echo "ERROR: bwfmetaedit executable not found in DMG."
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

  # Unmount and cleanup
  hdiutil detach "$MOUNT_POINT" -quiet || true
  rm -f "$DMG_FILE"

  echo "bwfmetaedit ${PINNED_VERSION} installed successfully"
fi

# Verify installed versions match expected versions (fail if mismatch)
echo "Verifying installed versions match expected versions..."
HAS_VERSION_MISMATCH=0

INSTALLED_FLAC=$(brew list --versions flac | awk '{print $2}')
INSTALLED_MEDIAINFO=$(brew list --versions media-info | awk '{print $2}')
INSTALLED_ID3V2=$(brew list --versions id3v2 | awk '{print $2}')
INSTALLED_BWFMETAEDIT=$(brew list --versions bwfmetaedit 2>/dev/null | awk '{print $2}' || echo "not installed")

# Function to check version match (allows patch version differences for compatibility)
check_version_match() {
  local installed=$1
  local expected=$2
  local package=$3

  if [ -z "$installed" ] || [ "$installed" = "not installed" ]; then
    echo "ERROR: $package: version check failed (not installed or version not found)"
    return 1
  fi

  # Extract major.minor version for comparison (e.g., "1.4.3" -> "1.4")
  INSTALLED_MAJOR_MINOR=$(echo "$installed" | cut -d. -f1,2)
  EXPECTED_MAJOR_MINOR=$(echo "$expected" | cut -d. -f1,2)

  if [ "$INSTALLED_MAJOR_MINOR" != "$EXPECTED_MAJOR_MINOR" ]; then
    echo "ERROR: $package: version mismatch (expected ${expected}, got ${installed})"
    return 1
  fi

  echo "  ✓ $package: ${installed} (matches expected ${expected})"
  return 0
}

if ! check_version_match "$INSTALLED_FLAC" "$PINNED_FLAC" "flac"; then
  HAS_VERSION_MISMATCH=1
fi

if ! check_version_match "$INSTALLED_MEDIAINFO" "$PINNED_MEDIAINFO" "media-info"; then
  HAS_VERSION_MISMATCH=1
fi

if ! check_version_match "$INSTALLED_ID3V2" "$PINNED_ID3V2" "id3v2"; then
  HAS_VERSION_MISMATCH=1
fi

if ! check_version_match "$INSTALLED_BWFMETAEDIT" "$PINNED_BWFMETAEDIT" "bwfmetaedit"; then
  HAS_VERSION_MISMATCH=1
fi

if [ $HAS_VERSION_MISMATCH -eq 1 ]; then
  echo ""
  echo "ERROR: Installed versions do not match expected versions from system-dependencies.toml"
  echo "This ensures reproducibility - update system-dependencies.toml with the actual installed versions"
  echo "or ensure Homebrew has the expected versions available."
  exit 1
fi

echo "Verifying installed tools are available in PATH..."
MISSING_TOOLS=()
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
  echo "Note: On macOS, you may need to add Homebrew's bin directory to PATH:"
  echo "  export PATH=\"/opt/homebrew/bin:\$PATH\"  # Apple Silicon"
  echo "  export PATH=\"/usr/local/bin:\$PATH\"     # Intel"
  exit 1
fi

echo "All system dependencies installed successfully!"

