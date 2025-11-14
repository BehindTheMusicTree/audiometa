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

# Install bwfmetaedit using shared script
echo "Installing bwfmetaedit..."
"${SCRIPT_DIR}/ci/install-bwfmetaedit-ubuntu.sh"

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


