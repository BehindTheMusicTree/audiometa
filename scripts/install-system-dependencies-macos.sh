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

# Source common utilities
source "${SCRIPT_DIR}/ci/macos-common.sh"

# Install each package using focused scripts
echo "Installing ffmpeg..."
"${SCRIPT_DIR}/ci/install-ffmpeg-macos.sh" "${PINNED_FFMPEG}"

echo "Installing mediainfo..."
"${SCRIPT_DIR}/ci/install-mediainfo-macos.sh" "${PINNED_MEDIAINFO}"

echo "Installing flac..."
"${SCRIPT_DIR}/ci/install-flac-macos.sh" "${PINNED_FLAC}"

echo "Installing id3v2..."
"${SCRIPT_DIR}/ci/install-id3v2-macos.sh" "${PINNED_ID3V2}"

echo "Installing bwfmetaedit..."
"${SCRIPT_DIR}/ci/install-bwfmetaedit-macos.sh" "${PINNED_BWFMETAEDIT}"

# Verify installed versions match pinned versions
echo "Verifying installed versions..."
INSTALLED_FLAC=$(get_tool_version "flac")
INSTALLED_MEDIAINFO=$(get_tool_version "mediainfo")
INSTALLED_ID3V2=$(get_tool_version "id3v2")
INSTALLED_BWFMETAEDIT=$(get_tool_version "bwfmetaedit")

echo "  flac: ${INSTALLED_FLAC:-not found} (expected: ${PINNED_FLAC})"
echo "  mediainfo: ${INSTALLED_MEDIAINFO:-not found} (expected: ${PINNED_MEDIAINFO})"
echo "  id3v2: ${INSTALLED_ID3V2:-not found} (expected: ${PINNED_ID3V2})"
echo "  bwfmetaedit: ${INSTALLED_BWFMETAEDIT:-not found} (expected: ${PINNED_BWFMETAEDIT})"

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

if [ "$VERSION_MISMATCH" -eq 1 ]; then
  echo ""
  echo "ERROR: Version verification failed. Installed versions don't match pinned versions."
  exit 1
fi

echo "All installed versions match pinned versions."

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
