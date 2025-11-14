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

# Check installed versions and remove if different
PACKAGES_TO_INSTALL=()
for package in ffmpeg flac mediainfo; do
  var_name="PINNED_${package^^}"
  pinned_version="${!var_name}"

  if command -v "$package" &>/dev/null; then
    INSTALLED_VERSION=""
    case "$package" in
      ffmpeg)
        INSTALLED_VERSION=$(ffmpeg -version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
        ;;
      flac)
        INSTALLED_VERSION=$(flac --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
        ;;
      mediainfo)
        INSTALLED_VERSION=$(mediainfo --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
        ;;
    esac

    if [ -n "$INSTALLED_VERSION" ]; then
      # Compare installed version with pinned version (extract epoch:version-release format)
      INSTALLED_APT_VERSION=$(dpkg -l | grep "^ii.*${package}" | awk '{print $3}' || echo "")
      if [ -n "$INSTALLED_APT_VERSION" ] && [ "$INSTALLED_APT_VERSION" = "$pinned_version" ]; then
        echo "${package} ${INSTALLED_APT_VERSION} already installed (matches pinned version)"
        continue
      else
        echo "Removing existing ${package} version ${INSTALLED_APT_VERSION:-$INSTALLED_VERSION} (installing pinned version ${pinned_version})..."
        sudo apt-get remove -y "$package" 2>/dev/null || true
      fi
    fi
  fi

  PACKAGES_TO_INSTALL+=("${package}=${pinned_version}")
done

# Install packages if any need installation
if [ ${#PACKAGES_TO_INSTALL[@]} -gt 0 ]; then
  sudo apt-get install -y "${PACKAGES_TO_INSTALL[@]}" || {
    echo "ERROR: Failed to install pinned versions."
    echo "This may indicate the versions are no longer available."
    exit 1
  }
fi

# Install id3v2 using shared script
echo "Installing id3v2..."
"${SCRIPT_DIR}/install-id3v2-linux.sh" "${PINNED_ID3V2}"

echo "Installing bwfmetaedit..."

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
NEED_INSTALL=1
if command -v bwfmetaedit &>/dev/null; then
  # Check exact deb package version (matches conftest.py verification)
  INSTALLED_DEB_VERSION=$(dpkg -l | grep "^ii.*bwfmetaedit" | awk '{print $3}' || echo "")

  if [ -n "$INSTALLED_DEB_VERSION" ]; then
    # Expected deb package version format: {version}-1 (e.g., 25.04.1-1)
    EXPECTED_DEB_VERSION="${PINNED_VERSION}-1"

    if [ "$INSTALLED_DEB_VERSION" = "$EXPECTED_DEB_VERSION" ]; then
      echo "bwfmetaedit ${INSTALLED_DEB_VERSION} already installed (matches pinned version ${PINNED_VERSION})"
      NEED_INSTALL=0
    else
      echo "Removing existing bwfmetaedit version ${INSTALLED_DEB_VERSION} (installing pinned version ${PINNED_VERSION})..."
      sudo apt-get remove -y bwfmetaedit 2>/dev/null || sudo dpkg -r bwfmetaedit 2>/dev/null || true
    fi
  else
    echo "bwfmetaedit installed but version could not be determined, removing..."
    sudo apt-get remove -y bwfmetaedit 2>/dev/null || sudo dpkg -r bwfmetaedit 2>/dev/null || true
  fi
fi

# Install if needed
if [ "$NEED_INSTALL" -eq 1 ]; then
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


