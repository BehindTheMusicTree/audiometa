#!/bin/bash
# Install bwfmetaedit for Ubuntu CI
# Pinned version from system-dependencies.toml (fails if not available, no fallback)
# See system-dependencies.toml for version configuration

set -e

# Load pinned versions from system-dependencies.toml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
eval "$(python3 "${SCRIPT_DIR}/load-system-dependency-versions.py" bash)"

# Detect Ubuntu version from /etc/os-release
UBUNTU_VERSION_FULL=$(grep VERSION_ID /etc/os-release | cut -d'"' -f2)
UBUNTU_VERSION=$(echo "${UBUNTU_VERSION_FULL}" | cut -d. -f1,2)
UBUNTU_MAJOR=$(echo "${UBUNTU_VERSION}" | cut -d. -f1)

# Get Ubuntu codename
UBUNTU_CODENAME=$(grep VERSION_CODENAME /etc/os-release 2>/dev/null | cut -d= -f2 || echo "")

echo "Detected Ubuntu version: ${UBUNTU_VERSION_FULL} (${UBUNTU_VERSION})"
if [ -n "${UBUNTU_CODENAME}" ]; then
  echo "Ubuntu codename: ${UBUNTU_CODENAME}"
fi

# Pinned version from system-dependencies.toml
PINNED_VERSION="${PINNED_BWFMETAEDIT}"

# Check if bwfmetaedit is already installed
if command -v bwfmetaedit &>/dev/null; then
  # Check exact deb package version (matches conftest.py verification)
  INSTALLED_DEB_VERSION=$(dpkg -l | grep "^ii.*bwfmetaedit" | awk '{print $3}' || echo "")

  if [ -n "$INSTALLED_DEB_VERSION" ]; then
    # Expected deb package version format: {version}-1 (e.g., 25.04.1-1)
    EXPECTED_DEB_VERSION="${PINNED_VERSION}-1"

    if [ "$INSTALLED_DEB_VERSION" = "$EXPECTED_DEB_VERSION" ]; then
      echo "bwfmetaedit ${INSTALLED_DEB_VERSION} already installed (matches pinned version ${PINNED_VERSION})"
      exit 0
    else
      echo "Removing existing bwfmetaedit version ${INSTALLED_DEB_VERSION} (installing pinned version ${PINNED_VERSION})..."
      sudo apt-get remove -y bwfmetaedit 2>/dev/null || sudo dpkg -r bwfmetaedit 2>/dev/null || true
    fi
  else
    echo "bwfmetaedit installed but version could not be determined, removing..."
    sudo apt-get remove -y bwfmetaedit 2>/dev/null || sudo dpkg -r bwfmetaedit 2>/dev/null || true
  fi
fi

# MediaArea URL format: bwfmetaedit_{version}-1_amd64.{prefix}{ubuntu_version}.deb
# Ubuntu 24.04+ uses "Ubuntu_" prefix (capital U), older versions use "xUbuntu_" (lowercase x)

# Determine URL based on Ubuntu version
if [ "${UBUNTU_MAJOR}" -ge 24 ]; then
  URL="https://mediaarea.net/download/binary/bwfmetaedit/${PINNED_VERSION}/bwfmetaedit_${PINNED_VERSION}-1_amd64.Ubuntu_${UBUNTU_VERSION}.deb"
  UBUNTU_FORMAT="${UBUNTU_VERSION}"
else
  URL="https://mediaarea.net/download/binary/bwfmetaedit/${PINNED_VERSION}/bwfmetaedit_${PINNED_VERSION}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb"
  UBUNTU_FORMAT="${UBUNTU_VERSION}"
fi

echo "Downloading bwfmetaedit version ${PINNED_VERSION} for Ubuntu ${UBUNTU_FORMAT} from MediaArea..."
wget "$URL"
DEB_FILE=$(basename "$URL")
echo "Installing ${DEB_FILE}..."
sudo dpkg -i "$DEB_FILE" || sudo apt-get install -f -y
rm -f "$DEB_FILE"
echo "bwfmetaedit ${PINNED_VERSION} installed successfully"


