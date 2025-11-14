#!/bin/bash
# Install system dependencies for macOS CI
# Pinned versions from .github/system-dependencies.toml (fails if not available, no fallback)
# See .github/system-dependencies.toml for version configuration

set -e

# Load pinned versions from .github/system-dependencies.toml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
eval "$(python3 "${SCRIPT_DIR}/load-system-dependency-versions.py" bash)"

echo "Installing pinned package versions..."

# Homebrew version pinning format: brew install package@version
brew install \
  ffmpeg@${PINNED_FFMPEG} \
  flac@${PINNED_FLAC} \
  mediainfo@${PINNED_MEDIAINFO} \
  bwfmetaedit@${PINNED_BWFMETAEDIT} \
  id3v2@${PINNED_ID3V2} || {
  echo "ERROR: Pinned versions not available."
  echo "Update .github/system-dependencies.toml with correct versions."
  echo "Check available versions with: brew info <package>"
  exit 1
}


