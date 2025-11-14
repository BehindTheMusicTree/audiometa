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
for package in ffmpeg flac mediainfo id3v2 libimage-exiftool-perl libsndfile1; do
  var_name="PINNED_${package^^}"
  var_name="${var_name//-/_}"
  pinned_version="${!var_name}"
  echo "Checking $package=$pinned_version..."

  # Check if package exists at all
  if ! apt-cache madison "$package" &>/dev/null || [ -z "$(apt-cache madison "$package" 2>/dev/null)" ]; then
    echo "ERROR: Package $package is not available in any repository."
    echo "You may need to enable universe/multiverse repositories or the package name has changed."
    HAS_ERRORS=1
    continue
  fi

  # Skip version check for "latest"
  if [ "$pinned_version" != "latest" ]; then
    # Check if specific version exists
    if ! apt-cache madison "$package" 2>/dev/null | grep -q "$pinned_version"; then
      echo "ERROR: Pinned version $pinned_version for $package is not available."
      echo "Available versions for $package:"
      apt-cache madison "$package" 2>/dev/null | head -5 || echo "  (could not list versions)"
      echo ""
      HAS_ERRORS=1
    fi
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
for package in ffmpeg flac mediainfo libsndfile1; do
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
      libsndfile1)
        # libsndfile1 doesn't have a version command, skip version check
        INSTALLED_VERSION=""
        ;;
    esac

    # Get installed apt version for comparison (works even if INSTALLED_VERSION is empty)
    INSTALLED_APT_VERSION=$(dpkg -l | grep "^ii.*${package}" | awk '{print $3}' || echo "")

    if [ "$pinned_version" = "latest" ]; then
      # For "latest", just check if package is installed
      if [ -n "$INSTALLED_APT_VERSION" ]; then
        echo "${package} ${INSTALLED_APT_VERSION} already installed (using latest)"
        continue
      fi
    elif [ -n "$INSTALLED_APT_VERSION" ] && [ "$INSTALLED_APT_VERSION" = "$pinned_version" ]; then
      echo "${package} ${INSTALLED_APT_VERSION} already installed (matches pinned version)"
      continue
    elif [ -n "$INSTALLED_APT_VERSION" ]; then
      echo "Removing existing ${package} version ${INSTALLED_APT_VERSION} (installing pinned version ${pinned_version})..."
      sudo apt-get remove -y "$package" 2>/dev/null || true
    fi
  fi

  if [ "$pinned_version" = "latest" ]; then
    PACKAGES_TO_INSTALL+=("${package}")
  else
    PACKAGES_TO_INSTALL+=("${package}=${pinned_version}")
  fi
done

# Install packages if any need installation
if [ ${#PACKAGES_TO_INSTALL[@]} -gt 0 ]; then
  sudo apt-get install -y "${PACKAGES_TO_INSTALL[@]}" || {
    echo "ERROR: Failed to install pinned versions."
    echo "This may indicate the versions are no longer available."
    exit 1
  }
fi

# Install libimage-exiftool-perl with pinned version
if [ -n "$PINNED_LIBIMAGE_EXIFTOOL_PERL" ]; then
  echo "Installing libimage-exiftool-perl=${PINNED_LIBIMAGE_EXIFTOOL_PERL}..."

  # Check if already installed with correct version
  if command -v exiftool &>/dev/null; then
    INSTALLED_APT_VERSION=$(dpkg -l | grep "^ii.*libimage-exiftool-perl" | awk '{print $3}' || echo "")
    if [ -n "$INSTALLED_APT_VERSION" ] && [ "$INSTALLED_APT_VERSION" = "$PINNED_LIBIMAGE_EXIFTOOL_PERL" ]; then
      echo "libimage-exiftool-perl ${INSTALLED_APT_VERSION} already installed (matches pinned version)"
    else
      echo "Removing existing libimage-exiftool-perl version ${INSTALLED_APT_VERSION:-unknown} (installing pinned version ${PINNED_LIBIMAGE_EXIFTOOL_PERL})..."
      sudo apt-get remove -y libimage-exiftool-perl 2>/dev/null || true
      sudo apt-get install -y "libimage-exiftool-perl=${PINNED_LIBIMAGE_EXIFTOOL_PERL}" || {
        echo "ERROR: Failed to install pinned version of libimage-exiftool-perl."
        exit 1
      }
    fi
  else
    sudo apt-get install -y "libimage-exiftool-perl=${PINNED_LIBIMAGE_EXIFTOOL_PERL}" || {
      echo "ERROR: Failed to install pinned version of libimage-exiftool-perl."
      exit 1
    }
  fi
fi

# Install id3v2 using shared script
echo "Installing id3v2..."
"${SCRIPT_DIR}/install-id3v2-linux.sh" "${PINNED_ID3V2}"

# Install bwfmetaedit using shared script
echo "Installing bwfmetaedit..."
"${SCRIPT_DIR}/ci/install-bwfmetaedit-ubuntu.sh"

echo "Verifying installed tools are available in PATH..."
MISSING_TOOLS=()
for tool in ffprobe flac metaflac mediainfo id3v2 exiftool; do
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


