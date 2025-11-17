#!/bin/bash
# Install system dependencies for Ubuntu CI
# Pinned versions from system-dependencies.toml (fails if not available, no fallback)

set -e

# Update package lists first
echo "Updating package lists..."
sudo apt-get update

# Load pinned versions from system-dependencies.toml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
eval "$(python3 "${SCRIPT_DIR}/load-system-dependency-versions.py" bash)"

echo "Installing pinned package versions..."

# Function to resolve partial version to full version
# If pinned_version is a partial version (e.g., "24.01"), find the first available
# version that starts with it (e.g., "24.01.1-1build2")
resolve_version() {
  local package="$1"
  local pinned_version="$2"

  # If version contains a hyphen, it's already a full version
  if [[ "$pinned_version" == *"-"* ]]; then
    echo "$pinned_version"
    return
  fi

  # For partial versions, find the first available version that starts with it
  # Extract version from apt-cache madison output (format: "package | version | repo")
  local available_version=$(apt-cache madison "$package" 2>/dev/null | \
    awk -v prefix="$pinned_version" '{
      # Extract version from second column (between |)
      gsub(/^[^|]*\|[[:space:]]*/, "")
      gsub(/[[:space:]]*\|.*$/, "")
      version = $0
      # Check if version starts with prefix (handle epoch prefix like "7:")
      if (version ~ "^[0-9]+:" prefix || version ~ "^" prefix) {
        print version
        exit
      }
    }' | head -n1)

  if [ -n "$available_version" ]; then
    echo "$available_version"
  else
    # If no match found, return original (will fail later with better error)
    echo "$pinned_version"
  fi
}

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
    # Resolve partial version to full version for checking
    resolved_version=$(resolve_version "$package" "$pinned_version")

    # Check if resolved version exists (or if partial version matches any available version)
    if [ "$resolved_version" = "$pinned_version" ] && [[ "$pinned_version" != *"-"* ]]; then
      # Partial version that couldn't be resolved - check if any version starts with it
      if ! apt-cache madison "$package" 2>/dev/null | grep -qE "(^|[[:space:]]\|[[:space:]]*)([0-9]+:)?${pinned_version}"; then
        echo "ERROR: Pinned version $pinned_version for $package is not available."
        echo "Available versions for $package:"
        apt-cache madison "$package" 2>/dev/null | head -5 || echo "  (could not list versions)"
        echo ""
        HAS_ERRORS=1
      fi
    elif [ "$resolved_version" != "$pinned_version" ]; then
      # Partial version was resolved - verify resolved version exists
      if ! apt-cache madison "$package" 2>/dev/null | grep -qF "$resolved_version"; then
        echo "ERROR: Resolved version $resolved_version for $package (from pinned $pinned_version) is not available."
        echo "Available versions for $package:"
        apt-cache madison "$package" 2>/dev/null | head -5 || echo "  (could not list versions)"
        echo ""
        HAS_ERRORS=1
      fi
    else
      # Full version - check if it exists
      if ! apt-cache madison "$package" 2>/dev/null | grep -q "$pinned_version"; then
        echo "ERROR: Pinned version $pinned_version for $package is not available."
        echo "Available versions for $package:"
        apt-cache madison "$package" 2>/dev/null | head -5 || echo "  (could not list versions)"
        echo ""
        HAS_ERRORS=1
      fi
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

  # Resolve partial version to full version for installation
  resolved_version=$(resolve_version "$package" "$pinned_version")

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
    elif [ -n "$INSTALLED_APT_VERSION" ]; then
      # Check if installed version matches pinned version (using flexible matching)
      # Extract upstream version (before first '-') for comparison
      installed_upstream="${INSTALLED_APT_VERSION%%-*}"
      resolved_upstream="${resolved_version%%-*}"

      # Normalize versions (remove +dfsg, +ds suffixes and revision suffixes)
      installed_normalized="${installed_upstream%%+*}"
      installed_normalized="${installed_normalized%%_*}"
      resolved_normalized="${resolved_upstream%%+*}"
      resolved_normalized="${resolved_normalized%%_*}"

      # Check if versions match (exact or prefix match)
      if [ "$installed_normalized" = "$resolved_normalized" ] || \
         [[ "$installed_normalized" == "$resolved_normalized".* ]] || \
         [[ "$resolved_normalized" == "$installed_normalized".* ]]; then
        echo "${package} ${INSTALLED_APT_VERSION} already installed (matches pinned version ${pinned_version})"
        continue
      else
        echo "Removing existing ${package} version ${INSTALLED_APT_VERSION} (installing pinned version ${pinned_version} -> ${resolved_version})..."
        sudo apt-get remove -y "$package" 2>/dev/null || true
      fi
    fi
  fi

  if [ "$pinned_version" = "latest" ]; then
    PACKAGES_TO_INSTALL+=("${package}")
  else
    PACKAGES_TO_INSTALL+=("${package}=${resolved_version}")
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
"${SCRIPT_DIR}/install-bwfmetaedit-ubuntu.sh"

# Install PowerShell Core (required for PowerShell script linting in pre-commit hooks)
echo "Installing PowerShell Core..."
if command -v pwsh &>/dev/null; then
  echo "  PowerShell Core already installed"
else
  echo "  Installing PowerShell Core via Microsoft repository..."
  # Add Microsoft repository for PowerShell
  sudo apt-get update
  sudo apt-get install -y wget apt-transport-https software-properties-common || {
    echo "ERROR: Failed to install prerequisites for PowerShell installation."
    exit 1
  }

  # Download and install Microsoft repository key
  wget -q https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb || {
    echo "ERROR: Failed to download Microsoft repository configuration."
    exit 1
  }
  sudo dpkg -i packages-microsoft-prod.deb || {
    echo "ERROR: Failed to install Microsoft repository configuration."
    rm -f packages-microsoft-prod.deb
    exit 1
  }
  rm -f packages-microsoft-prod.deb

  # Update package lists and install PowerShell
  sudo apt-get update
  sudo apt-get install -y powershell || {
    echo "ERROR: Failed to install PowerShell Core."
    echo "Install manually: https://github.com/PowerShell/PowerShell#get-powershell"
    exit 1
  }
fi

# Verify PowerShell installation
if ! command -v pwsh &>/dev/null; then
  echo "WARNING: PowerShell Core installed but not found in PATH."
  echo "You may need to restart your terminal or check installation."
fi

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

# Verify installed versions match pinned versions using shared Python script
echo ""
echo "Verifying installed versions match pinned versions..."
if ! python3 "${SCRIPT_DIR}/verify-system-dependency-versions.py"; then
  echo ""
  echo "ERROR: Version verification failed. Installed versions don't match pinned versions."
  exit 1
fi

echo "All system dependencies installed successfully!"
