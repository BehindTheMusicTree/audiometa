#!/bin/bash
# Install system dependencies for Ubuntu CI
# Pinned versions from .github/system-dependencies.toml (fails if not available, no fallback)

set -e

# Load pinned versions from .github/system-dependencies.toml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
eval "$(python3 "${SCRIPT_DIR}/load-system-dependency-versions.py" bash)"

echo "Installing pinned package versions..."
sudo apt-get install -y \
  ffmpeg="$PINNED_FFMPEG" \
  flac="$PINNED_FLAC" \
  mediainfo="$PINNED_MEDIAINFO" \
  id3v2="$PINNED_ID3V2" || {
  echo "ERROR: Pinned versions not available."
  echo "Update .github/system-dependencies.toml with correct versions."
  exit 1
}

echo "Installing bwfmetaedit (pinned version)..."

# Try installing from Ubuntu repos first
if sudo apt-get install -y bwfmetaedit 2>/dev/null; then
  echo "bwfmetaedit installed from Ubuntu repos"
else
  # If not in repos, download pinned version from MediaArea
  # Detect Ubuntu version from /etc/os-release
  UBUNTU_VERSION=$(grep VERSION_ID /etc/os-release | cut -d'"' -f2 | cut -d. -f1,2)
  echo "Detected Ubuntu version: ${UBUNTU_VERSION}"

  # Pinned version from .github/system-dependencies.toml (must be available, no fallback)
  PINNED_VERSION="${PINNED_BWFMETAEDIT}"
  URL="https://mediaarea.net/download/binary/bwfmetaedit/${PINNED_VERSION}/bwfmetaedit_${PINNED_VERSION}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb"

  if ! wget -q --spider "$URL" 2>/dev/null; then
    echo "ERROR: Pinned bwfmetaedit version ${PINNED_VERSION} not available for Ubuntu ${UBUNTU_VERSION}"
    echo "URL: $URL"
    exit 1
  fi

  echo "Installing pinned bwfmetaedit version ${PINNED_VERSION} for Ubuntu ${UBUNTU_VERSION}"
  wget "$URL"
  sudo dpkg -i bwfmetaedit_${PINNED_VERSION}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb || sudo apt-get install -f -y
  rm bwfmetaedit_${PINNED_VERSION}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb
fi

echo "All system dependencies installed successfully!"


