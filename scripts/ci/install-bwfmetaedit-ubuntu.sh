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
# Try different URL patterns that MediaArea might use
URL_PATTERNS=(
  "https://mediaarea.net/download/binary/bwfmetaedit/${PINNED_VERSION}/bwfmetaedit_${PINNED_VERSION}-1_amd64.Ubuntu_${UBUNTU_VERSION}.deb"
  "https://mediaarea.net/download/binary/bwfmetaedit/${PINNED_VERSION}/bwfmetaedit_${PINNED_VERSION}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb"
)

URL=""
for url_pattern in "${URL_PATTERNS[@]}"; do
  if wget -q --spider "$url_pattern" 2>/dev/null; then
    URL="$url_pattern"
    break
  fi
done

if [ -z "$URL" ]; then
  echo "ERROR: bwfmetaedit version ${PINNED_VERSION} not available for Ubuntu ${UBUNTU_VERSION}"
  echo ""
  echo "Tried URLs:"
  for url_pattern in "${URL_PATTERNS[@]}"; do
    echo "  - $url_pattern"
  done
  echo ""
  echo "To find available versions:"
  echo "  1. Visit https://mediaarea.net/BWFMetaEdit/Download/Ubuntu"
  echo "  2. Check available versions for Ubuntu ${UBUNTU_VERSION}"
  echo "  3. Update system-dependencies.toml with the correct pinned_version"
  exit 1
fi

echo "Downloading bwfmetaedit version ${PINNED_VERSION} for Ubuntu ${UBUNTU_VERSION} from MediaArea..."
wget "$URL"
DEB_FILE=$(basename "$URL")
echo "Installing ${DEB_FILE}..."
sudo dpkg -i "$DEB_FILE" || sudo apt-get install -f -y
rm -f "$DEB_FILE"
echo "bwfmetaedit ${PINNED_VERSION} installed successfully"


