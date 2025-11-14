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

  # Try different URL patterns that MediaArea might use
  URL_PATTERNS=(
    "https://mediaarea.net/download/binary/bwfmetaedit/${PINNED_VERSION}/bwfmetaedit_${PINNED_VERSION}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb"
    "https://mediaarea.net/download/binary/bwfmetaedit/${PINNED_VERSION}/bwfmetaedit_${PINNED_VERSION}_amd64.xUbuntu_${UBUNTU_VERSION}.deb"
  )

  URL=""
  for url_pattern in "${URL_PATTERNS[@]}"; do
    if wget -q --spider "$url_pattern" 2>/dev/null; then
      URL="$url_pattern"
      break
    fi
  done

  if [ -z "$URL" ]; then
    echo "ERROR: Pinned bwfmetaedit version ${PINNED_VERSION} not available for Ubuntu ${UBUNTU_VERSION}"
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

  echo "Installing pinned bwfmetaedit version ${PINNED_VERSION} for Ubuntu ${UBUNTU_VERSION}"
  wget "$URL"
  sudo dpkg -i bwfmetaedit_${PINNED_VERSION}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb 2>/dev/null || \
    sudo dpkg -i bwfmetaedit_${PINNED_VERSION}_amd64.xUbuntu_${UBUNTU_VERSION}.deb || \
    sudo apt-get install -f -y
  rm -f bwfmetaedit_${PINNED_VERSION}*.deb
fi


