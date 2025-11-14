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
# Install ffmpeg with version pinning
echo "Installing ffmpeg@${PINNED_FFMPEG}..."
brew install ffmpeg@${PINNED_FFMPEG} || {
  echo "ERROR: Pinned ffmpeg version ${PINNED_FFMPEG} not available."
  echo "Check available versions with: brew search ffmpeg"
  exit 1
}

# Install packages without version pinning (Homebrew doesn't support @version for these)
# Note: mediainfo is called media-info in Homebrew
# We'll verify installed versions match expected versions after installation
echo "Installing flac, media-info, id3v2, bwfmetaedit..."
brew install flac media-info id3v2 bwfmetaedit || {
  echo "ERROR: Failed to install packages."
  echo "Check available packages with: brew search <package>"
  exit 1
}

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

