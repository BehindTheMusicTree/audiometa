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
echo "Installing flac, media-info, id3v2, bwfmetaedit (latest available versions)..."
brew install flac media-info id3v2 bwfmetaedit || {
  echo "ERROR: Failed to install packages."
  echo "Check available packages with: brew search <package>"
  exit 1
}

# Verify installed versions match expectations (informational only)
echo "Verifying installed versions..."
INSTALLED_FLAC=$(brew list --versions flac | awk '{print $2}')
INSTALLED_MEDIAINFO=$(brew list --versions media-info | awk '{print $2}')
INSTALLED_ID3V2=$(brew list --versions id3v2 | awk '{print $2}')
INSTALLED_BWFMETAEDIT=$(brew list --versions bwfmetaedit 2>/dev/null | awk '{print $2}' || echo "not installed")

echo "  flac: ${INSTALLED_FLAC} (expected: ${PINNED_FLAC})"
echo "  media-info: ${INSTALLED_MEDIAINFO} (expected: ${PINNED_MEDIAINFO})"
echo "  id3v2: ${INSTALLED_ID3V2} (expected: ${PINNED_ID3V2})"
echo "  bwfmetaedit: ${INSTALLED_BWFMETAEDIT} (expected: ${PINNED_BWFMETAEDIT})"

# Note: We can't enforce exact version matching for these packages since Homebrew
# doesn't support version pinning. The versions are documented in system-dependencies.toml
# for reference, but may differ from what's actually installed.


