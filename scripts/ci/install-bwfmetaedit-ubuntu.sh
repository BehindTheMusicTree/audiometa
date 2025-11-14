#!/bin/bash
# Install bwfmetaedit for Ubuntu CI
# Pinned version from system-dependencies.toml (fails if not available, no fallback)
# See system-dependencies.toml for version configuration

set -e

# Load pinned versions from system-dependencies.toml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
eval "$(python3 "${SCRIPT_DIR}/load-system-dependency-versions.py" bash)"

# Try installing from Ubuntu repos first
if sudo apt-get install -y bwfmetaedit 2>/dev/null; then
  echo "bwfmetaedit installed from Ubuntu repos"
else
  # If not in repos, download pinned version from MediaArea
  # Detect Ubuntu version from /etc/os-release
  UBUNTU_VERSION=$(grep VERSION_ID /etc/os-release | cut -d'"' -f2 | cut -d. -f1,2)
  echo "Detected Ubuntu version: ${UBUNTU_VERSION}"

  # Pinned version from system-dependencies.toml
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


