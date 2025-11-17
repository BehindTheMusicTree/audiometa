#!/bin/bash
# Shared utilities for macOS installation scripts

# Function to check and install Xcode Command Line Tools if needed
check_and_install_build_tools() {
  if command -v make &>/dev/null && command -v gcc &>/dev/null; then
    return 0
  fi

  echo "Build tools (make, gcc) not found. Checking for Xcode Command Line Tools..."

  # Check if Command Line Tools are installed by checking for a tool they provide
  if [ -d "/Library/Developer/CommandLineTools" ]; then
    echo "Command Line Tools directory exists but tools not in PATH. Checking PATH..."
    # Tools might be installed but not in PATH - try to find them
    if [ -f "/Library/Developer/CommandLineTools/usr/bin/make" ] && [ -f "/Library/Developer/CommandLineTools/usr/bin/gcc" ]; then
      echo "Command Line Tools found but not in PATH. Adding to PATH..."
      export PATH="/Library/Developer/CommandLineTools/usr/bin:$PATH"
      if [ -n "$GITHUB_PATH" ]; then
        echo "/Library/Developer/CommandLineTools/usr/bin" >> "$GITHUB_PATH"
      fi
      return 0
    fi
  fi

  # Check if xcode-select can find them
  if xcode-select -p &>/dev/null; then
    XCODE_PATH=$(xcode-select -p)
    if [ -f "${XCODE_PATH}/usr/bin/make" ] && [ -f "${XCODE_PATH}/usr/bin/gcc" ]; then
      echo "Xcode tools found at ${XCODE_PATH}. Adding to PATH..."
      export PATH="${XCODE_PATH}/usr/bin:$PATH"
      if [ -n "$GITHUB_PATH" ]; then
        echo "${XCODE_PATH}/usr/bin" >> "$GITHUB_PATH"
      fi
      return 0
    fi
  fi

  # If we get here, Command Line Tools are not installed
  echo "Xcode Command Line Tools not found. Attempting to install..."

  # Try to install (this will open a GUI dialog on macOS, which won't work in CI)
  # In CI environments, this should already be installed
  if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    echo "ERROR: Build tools not found in CI environment."
    echo "Xcode Command Line Tools should be pre-installed in CI."
    echo "Please ensure the CI environment has Command Line Tools installed."
    exit 1
  fi

  # For local development, try to trigger installation
  echo "Triggering Xcode Command Line Tools installation..."
  echo "Note: This will open a GUI dialog. Please follow the prompts to install."

  # Try to trigger installation (returns 0 if dialog opened, 1 if already installed/installing)
  if xcode-select --install 2>&1; then
    echo ""
    echo "Installation dialog opened. Please:"
    echo "1. Complete the installation in the dialog that appeared"
    echo "2. Wait for installation to finish (this may take several minutes)"
    echo "3. Run this script again"
    echo ""
    echo "Alternatively, you can install manually by running:"
    echo "  xcode-select --install"
    exit 1
  else
    # Installation dialog might already be open, or tools might be installing
    echo "Installation may already be in progress, or dialog is already open."
    echo "Please complete the installation and run this script again."
    echo ""
    echo "To check installation status, run:"
    echo "  xcode-select -p"
    exit 1
  fi
}

# Function to check if a tool version matches pinned version (major.minor)
check_version_match() {
  local tool_name="$1"
  local installed_version="$2"
  local pinned_version="$3"

  if [ -z "$installed_version" ] || [ "$installed_version" = "not found" ]; then
    return 1
  fi

  local installed_major_minor=$(echo "$installed_version" | cut -d. -f1,2)
  local pinned_major_minor=$(echo "$pinned_version" | cut -d. -f1,2)

  if [ "$installed_major_minor" = "$pinned_major_minor" ]; then
    return 0
  else
    return 1
  fi
}

# Function to find tool executable path (checks common installation locations)
find_tool_path() {
  local tool_name="$1"
  local tool_path
  local homebrew_prefix

  # First try command -v (checks PATH)
  if command -v "$tool_name" &>/dev/null; then
    command -v "$tool_name"
    return 0
  fi

  # Check common installation paths
  for path in "/usr/local/bin/${tool_name}" "/opt/local/bin/${tool_name}" "/opt/homebrew/bin/${tool_name}"; do
    if [ -f "$path" ] && [ -x "$path" ]; then
      echo "$path"
      return 0
    fi
  done

  # Special handling for ffmpeg/ffprobe (keg-only packages)
  if [ "$tool_name" = "ffmpeg" ] || [ "$tool_name" = "ffprobe" ]; then
    homebrew_prefix=$(get_homebrew_prefix)
    # Check common ffmpeg versioned paths
    for version in "7" "6" "5"; do
      path="${homebrew_prefix}/opt/ffmpeg@${version}/bin/${tool_name}"
      if [ -f "$path" ] && [ -x "$path" ]; then
        echo "$path"
        return 0
      fi
    done
  fi

  return 1
}

# Function to get installed version of a tool
get_tool_version() {
  local tool_name="$1"
  local version_output
  local tool_path

  # Find the tool path
  tool_path=$(find_tool_path "$tool_name")
  if [ -z "$tool_path" ]; then
    echo ""
    return 1
  fi

  case "$tool_name" in
    flac|metaflac)
      version_output=$("$tool_path" --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
      ;;
    mediainfo)
      # mediainfo outputs: "MediaInfo Command line, MediaInfoLib - v25.10"
      version_output=$("$tool_path" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1 || echo "")
      ;;
    id3v2)
      version_output=$("$tool_path" --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
      ;;
    bwfmetaedit)
      version_output=$("$tool_path" --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
      ;;
    ffmpeg|ffprobe)
      version_output=$("$tool_path" -version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
      ;;
    exiftool)
      # exiftool outputs version as: "13.10" (just major.minor)
      version_output=$("$tool_path" -ver 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1 || echo "")
      ;;
    *)
      version_output=""
      ;;
  esac

  echo "$version_output"
}

# Function to get Homebrew prefix (handles both Intel and Apple Silicon)
get_homebrew_prefix() {
  if command -v brew &>/dev/null; then
    brew --prefix 2>/dev/null || echo "/opt/homebrew"
  else
    # Fallback: detect based on architecture
    if [ "$(uname -m)" = "arm64" ]; then
      echo "/opt/homebrew"
    else
      echo "/usr/local"
    fi
  fi
}

# Function to remove Homebrew installation of a package
remove_homebrew_package() {
  local package_name="$1"
  local binary_paths="$2"  # Space-separated list of binary paths to remove

  brew uninstall "$package_name" 2>/dev/null || true

  if [ -n "$binary_paths" ]; then
    for binary_path in $binary_paths; do
      rm -f "$binary_path" 2>/dev/null || true
      # Also check opt/homebrew for Apple Silicon
      if [[ "$binary_path" == /usr/local/bin/* ]]; then
        rm -f "/opt/homebrew${binary_path#/usr/local}" 2>/dev/null || true
      fi
    done
  fi
}
