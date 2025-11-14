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
if [ -z "$PINNED_FFMPEG" ] || [ -z "$PINNED_FLAC" ] || [ -z "$PINNED_MEDIAINFO" ] || [ -z "$PINNED_ID3V2" ] || [ -z "$PINNED_BWFMETAEDIT" ] || [ -z "$PINNED_EXIFTOOL" ]; then
  echo "ERROR: Failed to load all required versions from system-dependencies.toml"
  echo "Loaded versions:"
  echo "  PINNED_FFMPEG=${PINNED_FFMPEG:-NOT SET}"
  echo "  PINNED_FLAC=${PINNED_FLAC:-NOT SET}"
  echo "  PINNED_MEDIAINFO=${PINNED_MEDIAINFO:-NOT SET}"
  echo "  PINNED_ID3V2=${PINNED_ID3V2:-NOT SET}"
  echo "  PINNED_BWFMETAEDIT=${PINNED_BWFMETAEDIT:-NOT SET}"
  echo "  PINNED_EXIFTOOL=${PINNED_EXIFTOOL:-NOT SET}"
  exit 1
fi

# Source common utilities
source "${SCRIPT_DIR}/ci/macos-common.sh"

HOMEBREW_PREFIX=$(get_homebrew_prefix)

# Function to install a Homebrew package with version verification
install_homebrew_package() {
  local tool_name="$1"
  local brew_package="$2"
  local pinned_version="$3"
  local binary_paths="$4"  # Optional: space-separated list of binary paths to remove

  echo "Installing ${tool_name}..."

  # Check if already installed with correct version
  if command -v "$tool_name" &>/dev/null; then
    INSTALLED_VERSION=$(get_tool_version "$tool_name")
    if check_version_match "$tool_name" "$INSTALLED_VERSION" "$pinned_version"; then
      echo "  ${tool_name} ${INSTALLED_VERSION} already installed (matches pinned version ${pinned_version})"
      return 0
    else
      echo "  Removing existing ${tool_name} version ${INSTALLED_VERSION} (installing pinned version ${pinned_version})..."
      remove_homebrew_package "$brew_package" "$binary_paths"
    fi
  fi

  # Install via Homebrew
  brew install "$brew_package" || {
    echo "ERROR: Failed to install ${tool_name} via Homebrew."
    exit 1
  }

  # Verify installed version matches pinned version
  INSTALLED_VERSION=$(get_tool_version "$tool_name")
  if [ -z "$INSTALLED_VERSION" ]; then
    echo "ERROR: Failed to get installed ${tool_name} version."
    exit 1
  fi

  if ! check_version_match "$tool_name" "$INSTALLED_VERSION" "$pinned_version"; then
    echo "ERROR: Installed ${tool_name} version ${INSTALLED_VERSION} does not match pinned version ${pinned_version}."
    echo "Homebrew may have installed a different version than expected."
    exit 1
  fi

  echo "  ${tool_name} ${INSTALLED_VERSION} installed successfully (matches pinned version ${pinned_version})"
}

# Function to install ffmpeg (special case: uses @version syntax)
install_ffmpeg() {
  local pinned_version="$1"

  echo "Installing ffmpeg..."

  # Check if ffmpeg is already installed
  NEED_INSTALL=1
  if command -v ffmpeg &>/dev/null; then
    INSTALLED_VERSION=$(ffmpeg -version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")

    if [ -n "$INSTALLED_VERSION" ]; then
      INSTALLED_MAJOR=$(echo "$INSTALLED_VERSION" | cut -d. -f1)
      PINNED_MAJOR=$(echo "$pinned_version" | cut -d. -f1)

      if [ "$INSTALLED_MAJOR" = "$PINNED_MAJOR" ]; then
        echo "  ffmpeg ${INSTALLED_VERSION} already installed (matches pinned version ${pinned_version})"
        NEED_INSTALL=0
        # ffmpeg@7 is keg-only, ensure it's in PATH
        FFMPEG_BIN_PATH="${HOMEBREW_PREFIX}/opt/ffmpeg@${pinned_version}/bin"
        if [ -d "$FFMPEG_BIN_PATH" ]; then
          export PATH="$FFMPEG_BIN_PATH:$PATH"
          if [ -n "$GITHUB_PATH" ]; then
            echo "$FFMPEG_BIN_PATH" >> "$GITHUB_PATH"
          fi
        fi
      else
        echo "  Removing existing ffmpeg version ${INSTALLED_VERSION} (installing pinned version ${pinned_version})..."
        brew uninstall ffmpeg 2>/dev/null || brew uninstall ffmpeg@${INSTALLED_MAJOR} 2>/dev/null || true
      fi
    else
      echo "  ffmpeg installed but version could not be determined, removing..."
      brew uninstall ffmpeg 2>/dev/null || true
    fi
  fi

  # Install ffmpeg with version pinning if needed
  if [ "$NEED_INSTALL" -eq 1 ]; then
    echo "  Installing ffmpeg@${pinned_version}..."
    brew install ffmpeg@${pinned_version} || {
      echo "ERROR: Pinned ffmpeg version ${pinned_version} not available."
      echo "Check available versions with: brew search ffmpeg"
      exit 1
    }
    # ffmpeg@7 is keg-only, so we need to add it to PATH
    FFMPEG_BIN_PATH="${HOMEBREW_PREFIX}/opt/ffmpeg@${pinned_version}/bin"
    if [ -d "$FFMPEG_BIN_PATH" ]; then
      export PATH="$FFMPEG_BIN_PATH:$PATH"
      if [ -n "$GITHUB_PATH" ]; then
        echo "$FFMPEG_BIN_PATH" >> "$GITHUB_PATH"
      fi
    fi
  fi

  echo "  ffmpeg ${pinned_version} installed successfully"
}

echo "Installing pinned package versions..."

# Install ffmpeg (special case: uses @version syntax)
install_ffmpeg "${PINNED_FFMPEG}"

# Install other packages via Homebrew
install_homebrew_package "flac" "flac" "${PINNED_FLAC}" "/usr/local/bin/flac /usr/local/bin/metaflac"
install_homebrew_package "mediainfo" "media-info" "${PINNED_MEDIAINFO}" "/usr/local/bin/mediainfo"
install_homebrew_package "id3v2" "id3v2" "${PINNED_ID3V2}" "/usr/local/bin/id3v2"
install_homebrew_package "bwfmetaedit" "bwfmetaedit" "${PINNED_BWFMETAEDIT}" "/usr/local/bin/bwfmetaedit"

# Install exiftool via Homebrew
install_homebrew_package "exiftool" "exiftool" "${PINNED_EXIFTOOL}" "/usr/local/bin/exiftool"

# Ensure /usr/local/bin is in PATH for verification (tools may be installed there)
if [ -d "/usr/local/bin" ] && [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
  export PATH="/usr/local/bin:$PATH"
  if [ -n "$GITHUB_PATH" ]; then
    echo "/usr/local/bin" >> "$GITHUB_PATH"
  fi
fi

# Verify installed versions match pinned versions
echo ""
echo "Verifying installed versions..."
INSTALLED_FLAC=$(get_tool_version "flac")
INSTALLED_MEDIAINFO=$(get_tool_version "mediainfo")
INSTALLED_ID3V2=$(get_tool_version "id3v2")
INSTALLED_BWFMETAEDIT=$(get_tool_version "bwfmetaedit")
INSTALLED_EXIFTOOL=$(get_tool_version "exiftool")

echo "  flac: ${INSTALLED_FLAC:-not found} (expected: ${PINNED_FLAC})"
echo "  mediainfo: ${INSTALLED_MEDIAINFO:-not found} (expected: ${PINNED_MEDIAINFO})"
echo "  id3v2: ${INSTALLED_ID3V2:-not found} (expected: ${PINNED_ID3V2})"
echo "  bwfmetaedit: ${INSTALLED_BWFMETAEDIT:-not found} (expected: ${PINNED_BWFMETAEDIT})"
echo "  exiftool: ${INSTALLED_EXIFTOOL:-not found} (expected: ${PINNED_EXIFTOOL})"

# Verify versions match (exact match for major.minor)
VERSION_MISMATCH=0

if ! check_version_match "flac" "$INSTALLED_FLAC" "$PINNED_FLAC"; then
  echo "ERROR: flac version mismatch: installed ${INSTALLED_FLAC}, expected ${PINNED_FLAC}"
  VERSION_MISMATCH=1
fi

if ! check_version_match "mediainfo" "$INSTALLED_MEDIAINFO" "$PINNED_MEDIAINFO"; then
  echo "ERROR: mediainfo version mismatch: installed ${INSTALLED_MEDIAINFO}, expected ${PINNED_MEDIAINFO}"
  VERSION_MISMATCH=1
fi

if ! check_version_match "id3v2" "$INSTALLED_ID3V2" "$PINNED_ID3V2"; then
  echo "ERROR: id3v2 version mismatch: installed ${INSTALLED_ID3V2}, expected ${PINNED_ID3V2}"
  VERSION_MISMATCH=1
fi

if ! check_version_match "bwfmetaedit" "$INSTALLED_BWFMETAEDIT" "$PINNED_BWFMETAEDIT"; then
  echo "ERROR: bwfmetaedit version mismatch: installed ${INSTALLED_BWFMETAEDIT}, expected ${PINNED_BWFMETAEDIT}"
  VERSION_MISMATCH=1
fi

if ! check_version_match "exiftool" "$INSTALLED_EXIFTOOL" "$PINNED_EXIFTOOL"; then
  echo "ERROR: exiftool version mismatch: installed ${INSTALLED_EXIFTOOL}, expected ${PINNED_EXIFTOOL}"
  VERSION_MISMATCH=1
fi

if [ "$VERSION_MISMATCH" -eq 1 ]; then
  echo ""
  echo "ERROR: Version verification failed. Installed versions don't match pinned versions."
  exit 1
fi

echo "All installed versions match pinned versions."

echo ""
echo "Verifying installed tools are available in PATH..."
MISSING_TOOLS=()

# Check each tool, including ffprobe which comes from ffmpeg@7 (keg-only)
for tool in ffprobe flac metaflac mediainfo id3v2 exiftool; do
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
  echo "  export PATH=\"${HOMEBREW_PREFIX}/bin:\$PATH\""
  echo ""
  echo "Note: ffmpeg@7 is keg-only. If ffprobe is missing, ensure PATH includes:"
  echo "  export PATH=\"${HOMEBREW_PREFIX}/opt/ffmpeg@7/bin:\$PATH\""
  exit 1
fi

echo "All system dependencies installed successfully!"
