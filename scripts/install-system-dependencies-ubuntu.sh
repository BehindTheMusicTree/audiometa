#!/bin/bash
# Install system dependencies for Ubuntu CI
# Pinned versions from system-dependencies.toml (fails if not available, no fallback)

set -e

# Update package lists first
echo "Updating package lists..."
sudo apt-get update

# Load pinned versions from system-dependencies.toml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
eval "$(python3 "${SCRIPT_DIR}/ci/load-system-dependency-versions.py" bash)"

echo "Installing pinned package versions..."

# Check available versions before attempting installation
echo "Checking available package versions..."
HAS_ERRORS=0
for package in ffmpeg flac mediainfo id3v2; do
  var_name="PINNED_${package^^}"
  pinned_version="${!var_name}"
  echo "Checking $package=$pinned_version..."

  # Check if package exists at all
  if ! apt-cache madison "$package" &>/dev/null || [ -z "$(apt-cache madison "$package" 2>/dev/null)" ]; then
    echo "ERROR: Package $package is not available in any repository."
    echo "You may need to enable universe/multiverse repositories or the package name has changed."
    HAS_ERRORS=1
    continue
  fi

  # Check if specific version exists
  if ! apt-cache madison "$package" 2>/dev/null | grep -q "$pinned_version"; then
    echo "ERROR: Pinned version $pinned_version for $package is not available."
    echo "Available versions for $package:"
    apt-cache madison "$package" 2>/dev/null | head -5 || echo "  (could not list versions)"
    echo ""
    HAS_ERRORS=1
  fi
done

if [ $HAS_ERRORS -eq 1 ]; then
  echo ""
  echo "Update system-dependencies.toml with versions from the lists above."
  echo "Use the format from the first column (e.g., '7:8.0.2-1ubuntu1' for ffmpeg)."
  exit 1
fi

sudo apt-get install -y \
  ffmpeg="$PINNED_FFMPEG" \
  flac="$PINNED_FLAC" \
  mediainfo="$PINNED_MEDIAINFO" \
  id3v2="$PINNED_ID3V2" || {
  echo "ERROR: Failed to install pinned versions."
  echo "This may indicate the versions are no longer available."
  exit 1
}

echo "Installing bwfmetaedit..."

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
  exit 1
fi

echo "All system dependencies installed successfully!"


