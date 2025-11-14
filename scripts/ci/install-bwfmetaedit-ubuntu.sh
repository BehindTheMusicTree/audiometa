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
  INSTALLED_VERSION=$(bwfmetaedit --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "unknown")
  echo "Installed version: ${INSTALLED_VERSION}"
else
  # If not in repos, try to download from MediaArea
  # Detect Ubuntu version from /etc/os-release
  UBUNTU_VERSION=$(grep VERSION_ID /etc/os-release | cut -d'"' -f2 | cut -d. -f1,2)
  echo "Detected Ubuntu version: ${UBUNTU_VERSION}"
  echo "bwfmetaedit not found in Ubuntu repos, trying MediaArea..."

  # Pinned version from system-dependencies.toml
  PINNED_VERSION="${PINNED_BWFMETAEDIT}"

  # If pinned_version is "latest_available", try to find a compatible version
  if [ "${PINNED_VERSION}" = "latest_available" ]; then
    echo "No specific version pinned, checking MediaArea for available versions..."
    # Try common recent versions in reverse order (newest first)
    VERSIONS_TO_TRY=("24.12" "24.10" "24.05" "24.01" "23.10" "23.05")
    URL=""
    for version in "${VERSIONS_TO_TRY[@]}"; do
      URL_PATTERNS=(
        "https://mediaarea.net/download/binary/bwfmetaedit/${version}/bwfmetaedit_${version}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb"
        "https://mediaarea.net/download/binary/bwfmetaedit/${version}/bwfmetaedit_${version}_amd64.xUbuntu_${UBUNTU_VERSION}.deb"
      )
      for url_pattern in "${URL_PATTERNS[@]}"; do
        if wget -q --spider "$url_pattern" 2>/dev/null; then
          URL="$url_pattern"
          PINNED_VERSION="$version"
          echo "Found available version: ${version}"
          break 2
        fi
      done
    done
  else
    # Try different URL patterns that MediaArea might use for pinned version
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
  fi

  if [ -z "$URL" ]; then
    echo "ERROR: bwfmetaedit not available in Ubuntu repos and no compatible version found on MediaArea for Ubuntu ${UBUNTU_VERSION}"
    echo ""
    if [ "${PINNED_VERSION}" != "latest_available" ]; then
      echo "Tried pinned version: ${PINNED_VERSION}"
      echo "Tried URLs:"
      for url_pattern in "${URL_PATTERNS[@]}"; do
        echo "  - $url_pattern"
      done
    fi
    echo ""
    echo "To resolve this:"
    echo "  1. Check if bwfmetaedit is available in Ubuntu repos: apt-cache search bwfmetaedit"
    echo "  2. Visit https://mediaarea.net/BWFMetaEdit/Download/Ubuntu"
    echo "  3. Check available versions for Ubuntu ${UBUNTU_VERSION}"
    echo "  4. Update system-dependencies.toml with a compatible pinned_version or use 'latest_available'"
    exit 1
  fi

  echo "Installing bwfmetaedit version ${PINNED_VERSION} from MediaArea for Ubuntu ${UBUNTU_VERSION}"
  wget "$URL"
  DEB_FILE=$(basename "$URL")
  sudo dpkg -i "$DEB_FILE" || sudo apt-get install -f -y
  rm -f "$DEB_FILE"
fi


