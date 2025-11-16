#!/bin/bash
# Install system dependencies for macOS CI
# Pinned versions from system-dependencies.toml (fails if not available, no fallback)
# See system-dependencies.toml for version configuration

set -e

# Load pinned versions from system-dependencies.toml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION_OUTPUT=$(python3 "${SCRIPT_DIR}/load-system-dependency-versions.py" bash)
if [ $? -ne 0 ] || [ -z "$VERSION_OUTPUT" ]; then
  echo "ERROR: Failed to load versions from system-dependencies.toml"
  exit 1
fi
eval "$VERSION_OUTPUT"

# Verify versions were loaded
if [ -z "$PINNED_FFMPEG" ] || [ -z "$PINNED_FLAC" ] || [ -z "$PINNED_MEDIAINFO" ] || [ -z "$PINNED_ID3V2" ] || [ -z "$PINNED_BWFMETAEDIT" ] || [ -z "$PINNED_EXIFTOOL" ] || [ -z "$PINNED_LIBSNDFILE" ]; then
  echo "ERROR: Failed to load all required versions from system-dependencies.toml"
  echo "Loaded versions:"
  echo "  PINNED_FFMPEG=${PINNED_FFMPEG:-NOT SET}"
  echo "  PINNED_FLAC=${PINNED_FLAC:-NOT SET}"
  echo "  PINNED_MEDIAINFO=${PINNED_MEDIAINFO:-NOT SET}"
  echo "  PINNED_ID3V2=${PINNED_ID3V2:-NOT SET}"
  echo "  PINNED_BWFMETAEDIT=${PINNED_BWFMETAEDIT:-NOT SET}"
  echo "  PINNED_EXIFTOOL=${PINNED_EXIFTOOL:-NOT SET}"
  echo "  PINNED_LIBSNDFILE=${PINNED_LIBSNDFILE:-NOT SET}"
  exit 1
fi

# Source common utilities
source "${SCRIPT_DIR}/macos-common.sh"

HOMEBREW_PREFIX=$(get_homebrew_prefix)

# Update Homebrew to ensure we have the latest formula definitions
# This ensures consistency across CI runs - all runners will use the same formula versions
echo "Updating Homebrew to ensure latest formula definitions..."
brew update

# Function to install a Homebrew package with version verification
install_homebrew_package() {
  local tool_name="$1"
  local brew_package="$2"
  local pinned_version="$3"
  local binary_paths="$4"  # Optional: space-separated list of binary paths to remove

  echo "Installing ${tool_name}..."

  # Check if this is a library package (no executable) or executable tool
  local is_library=0
  local already_installed=0

  # Check if package is already installed via Homebrew
  if brew list "$brew_package" &>/dev/null; then
    already_installed=1
    # Check if it's a library (no executable) or executable tool
    if ! command -v "$tool_name" &>/dev/null; then
      is_library=1
    fi
  elif command -v "$tool_name" &>/dev/null; then
    # Executable exists but not via Homebrew (might be system-installed)
    already_installed=0
  fi

  # Check if already installed with correct version (after brew update)
  # We check after brew update to ensure we're comparing against the latest available version
  if [ "$already_installed" -eq 1 ]; then
    INSTALLED_VERSION=""
    if [ "$is_library" -eq 1 ]; then
      # For library packages, get version from pkg-config or brew info
      INSTALLED_VERSION=$(pkg-config --modversion "$brew_package" 2>/dev/null || brew info "$brew_package" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+(_[0-9]+)?' | head -n1 || echo "")
    else
      INSTALLED_VERSION=$(get_tool_version "$tool_name")
    fi

    if [ -n "$INSTALLED_VERSION" ] && check_version_match "$tool_name" "$INSTALLED_VERSION" "$pinned_version"; then
      # Version matches, but we still need to upgrade to ensure we have the latest from updated formulas
      # brew upgrade will be a no-op if already at latest, but ensures consistency
      echo "  ${tool_name} ${INSTALLED_VERSION} already installed (matches pinned version ${pinned_version})"
      echo "  Upgrading to ensure latest version from updated Homebrew formulas..."
      set +e
      brew upgrade "$brew_package" 2>&1 | grep -v "Already up-to-date" || true
      set -e
      # Continue to version verification below (don't return early)
    elif [ -n "$INSTALLED_VERSION" ]; then
      echo "  Removing existing ${tool_name} version ${INSTALLED_VERSION} (installing pinned version ${pinned_version})..."
      remove_homebrew_package "$brew_package" "$binary_paths"
      already_installed=0
    elif [ "$is_library" -eq 1 ]; then
      # For library packages, if we can't extract version but package is installed, upgrade and verify later
      echo "  ${tool_name} already installed via Homebrew, upgrading to latest..."
      set +e
      brew upgrade "$brew_package" 2>&1 | grep -v "Already up-to-date" || true
      set -e
      # Version verification will be done in the final verification section
      return 0
    fi
  fi

  # Install via Homebrew if not already installed
  if [ "$already_installed" -eq 0 ]; then
    set +e
    brew install "$brew_package" 2>&1
    local install_status=$?
    set -e

    if [ $install_status -ne 0 ]; then
      # Check if installation failed because package is already installed
      if brew list "$brew_package" &>/dev/null; then
        echo "  ${tool_name} already installed via Homebrew, upgrading to latest..."
        set +e
        brew upgrade "$brew_package" 2>&1 | grep -v "Already up-to-date" || true
        set -e
      else
        echo "ERROR: Failed to install ${tool_name} via Homebrew."
        exit 1
      fi
    fi
  fi

  # Verify installed version matches pinned version
  INSTALLED_VERSION=""
  if [ "$is_library" -eq 1 ] || ! command -v "$tool_name" &>/dev/null; then
    # For library packages, get version from pkg-config or brew info
    INSTALLED_VERSION=$(pkg-config --modversion "$brew_package" 2>/dev/null || brew info "$brew_package" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+(_[0-9]+)?' | head -n1 || echo "")
  else
    INSTALLED_VERSION=$(get_tool_version "$tool_name")
  fi

  if [ -z "$INSTALLED_VERSION" ]; then
    if [ "$is_library" -eq 1 ]; then
      # For library packages, if we can't extract version but package is installed, consider it OK
      # The final verification section will handle version checking
      echo "  ${tool_name} installed successfully (version verification will be done in final check)"
      return 0
    else
      echo "ERROR: Failed to get installed ${tool_name} version."
      exit 1
    fi
  fi

  if ! check_version_match "$tool_name" "$INSTALLED_VERSION" "$pinned_version"; then
    echo "ERROR: Installed ${tool_name} version ${INSTALLED_VERSION} does not match pinned version ${pinned_version}."
    echo "Homebrew may have installed a different version than expected."
    exit 1
  fi

  echo "  ${tool_name} ${INSTALLED_VERSION} installed successfully (matches pinned version ${pinned_version})"
}

# Function to install ffmpeg (special case: uses @version syntax)
install_ffmpeg() {
  local pinned_version="$1"

  echo "Installing ffmpeg..."

  # Check if ffmpeg is already installed
  NEED_INSTALL=1
  if command -v ffmpeg &>/dev/null; then
    INSTALLED_VERSION=$(ffmpeg -version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")

    if [ -n "$INSTALLED_VERSION" ]; then
      INSTALLED_MAJOR=$(echo "$INSTALLED_VERSION" | cut -d. -f1)
      PINNED_MAJOR=$(echo "$pinned_version" | cut -d. -f1)

      if [ "$INSTALLED_MAJOR" = "$PINNED_MAJOR" ]; then
        echo "  ffmpeg ${INSTALLED_VERSION} already installed (matches pinned version ${pinned_version})"
        NEED_INSTALL=0
        # ffmpeg@7 is keg-only, ensure it's in PATH
        FFMPEG_BIN_PATH="${HOMEBREW_PREFIX}/opt/ffmpeg@${pinned_version}/bin"
        if [ -d "$FFMPEG_BIN_PATH" ]; then
          export PATH="$FFMPEG_BIN_PATH:$PATH"
          if [ -n "$GITHUB_PATH" ]; then
            echo "$FFMPEG_BIN_PATH" >> "$GITHUB_PATH"
          fi
        fi
      else
        echo "  Removing existing ffmpeg version ${INSTALLED_VERSION} (installing pinned version ${pinned_version})..."
        brew uninstall ffmpeg 2>/dev/null || brew uninstall ffmpeg@${INSTALLED_MAJOR} 2>/dev/null || true
      fi
    else
      echo "  ffmpeg installed but version could not be determined, removing..."
      brew uninstall ffmpeg 2>/dev/null || true
    fi
  fi

  # Install ffmpeg with version pinning if needed
  if [ "$NEED_INSTALL" -eq 1 ]; then
    echo "  Installing ffmpeg@${pinned_version}..."
    brew install ffmpeg@${pinned_version} || {
      echo "ERROR: Pinned ffmpeg version ${pinned_version} not available."
      echo "Check available versions with: brew search ffmpeg"
      exit 1
    }
    # ffmpeg@7 is keg-only, so we need to add it to PATH
    FFMPEG_BIN_PATH="${HOMEBREW_PREFIX}/opt/ffmpeg@${pinned_version}/bin"
    if [ -d "$FFMPEG_BIN_PATH" ]; then
      export PATH="$FFMPEG_BIN_PATH:$PATH"
      if [ -n "$GITHUB_PATH" ]; then
        echo "$FFMPEG_BIN_PATH" >> "$GITHUB_PATH"
      fi
    fi
  fi

  echo "  ffmpeg ${pinned_version} installed successfully"
}

echo "Installing pinned package versions..."

# Install ffmpeg (special case: uses @version syntax)
install_ffmpeg "${PINNED_FFMPEG}"

# Install other packages via Homebrew
install_homebrew_package "flac" "flac" "${PINNED_FLAC}" "/usr/local/bin/flac /usr/local/bin/metaflac"
install_homebrew_package "mediainfo" "media-info" "${PINNED_MEDIAINFO}" "/usr/local/bin/mediainfo"
install_homebrew_package "id3v2" "id3v2" "${PINNED_ID3V2}" "/usr/local/bin/id3v2"
install_homebrew_package "bwfmetaedit" "bwfmetaedit" "${PINNED_BWFMETAEDIT}" "/usr/local/bin/bwfmetaedit"

# Install exiftool via Homebrew
install_homebrew_package "exiftool" "exiftool" "${PINNED_EXIFTOOL}" "/usr/local/bin/exiftool"

# Install libsndfile (required by soundfile Python package)
install_homebrew_package "libsndfile" "libsndfile" "${PINNED_LIBSNDFILE}" ""

# Ensure Homebrew bin directory is in PATH (tools are installed there)
HOMEBREW_BIN="${HOMEBREW_PREFIX}/bin"
if [ -d "$HOMEBREW_BIN" ] && [[ ":$PATH:" != *":${HOMEBREW_BIN}:"* ]]; then
  export PATH="${HOMEBREW_BIN}:$PATH"
  if [ -n "$GITHUB_PATH" ]; then
    echo "$HOMEBREW_BIN" >> "$GITHUB_PATH"
  fi
fi

# Ensure Homebrew opt/bin directories are in PATH (for keg-only packages and opt symlinks)
# Some packages create symlinks in opt/package/bin
for opt_package in flac; do
  OPT_BIN="${HOMEBREW_PREFIX}/opt/${opt_package}/bin"
  if [ -d "$OPT_BIN" ] && [[ ":$PATH:" != *":${OPT_BIN}:"* ]]; then
    export PATH="${OPT_BIN}:$PATH"
    if [ -n "$GITHUB_PATH" ]; then
      echo "$OPT_BIN" >> "$GITHUB_PATH"
    fi
  fi
done

# Ensure Homebrew Cellar directories are in PATH (for packages with multiple versions)
# When multiple versions are installed, tools may be in Cellar but not symlinked
# Add the pinned version's Cellar path to ensure tools are accessible
if [ -n "$PINNED_FLAC" ]; then
  FLAC_CELLAR_BIN="${HOMEBREW_PREFIX}/Cellar/flac/${PINNED_FLAC}/bin"
  if [ -d "$FLAC_CELLAR_BIN" ] && [[ ":$PATH:" != *":${FLAC_CELLAR_BIN}:"* ]]; then
    export PATH="${FLAC_CELLAR_BIN}:$PATH"
    if [ -n "$GITHUB_PATH" ]; then
      echo "$FLAC_CELLAR_BIN" >> "$GITHUB_PATH"
    fi
  fi
fi

# Also ensure /usr/local/bin is in PATH for backward compatibility
if [ -d "/usr/local/bin" ] && [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
  export PATH="/usr/local/bin:$PATH"
  if [ -n "$GITHUB_PATH" ]; then
    echo "/usr/local/bin" >> "$GITHUB_PATH"
  fi
fi

# Verify installed versions match pinned versions
echo ""
echo "Verifying installed versions..."
INSTALLED_FLAC=$(get_tool_version "flac")
INSTALLED_MEDIAINFO=$(get_tool_version "mediainfo")
INSTALLED_ID3V2=$(get_tool_version "id3v2")
INSTALLED_BWFMETAEDIT=$(get_tool_version "bwfmetaedit")
INSTALLED_EXIFTOOL=$(get_tool_version "exiftool")

# Verify libsndfile installation (library, not executable)
INSTALLED_LIBSNDFILE=""
if brew list libsndfile &>/dev/null; then
  INSTALLED_LIBSNDFILE=$(pkg-config --modversion libsndfile 2>/dev/null || brew info libsndfile 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "installed")
fi

echo "  flac: ${INSTALLED_FLAC:-not found} (expected: ${PINNED_FLAC})"
echo "  mediainfo: ${INSTALLED_MEDIAINFO:-not found} (expected: ${PINNED_MEDIAINFO})"
echo "  id3v2: ${INSTALLED_ID3V2:-not found} (expected: ${PINNED_ID3V2})"
echo "  bwfmetaedit: ${INSTALLED_BWFMETAEDIT:-not found} (expected: ${PINNED_BWFMETAEDIT})"
echo "  exiftool: ${INSTALLED_EXIFTOOL:-not found} (expected: ${PINNED_EXIFTOOL})"
echo "  libsndfile: ${INSTALLED_LIBSNDFILE:-not found} (expected: ${PINNED_LIBSNDFILE})"

# Verify versions match (exact match for major.minor)
VERSION_MISMATCH=0

if ! check_version_match "flac" "$INSTALLED_FLAC" "$PINNED_FLAC"; then
  echo "ERROR: flac version mismatch: installed ${INSTALLED_FLAC}, expected ${PINNED_FLAC}"
  VERSION_MISMATCH=1
fi

if ! check_version_match "mediainfo" "$INSTALLED_MEDIAINFO" "$PINNED_MEDIAINFO"; then
  echo "ERROR: mediainfo version mismatch: installed ${INSTALLED_MEDIAINFO}, expected ${PINNED_MEDIAINFO}"
  VERSION_MISMATCH=1
fi

if ! check_version_match "id3v2" "$INSTALLED_ID3V2" "$PINNED_ID3V2"; then
  echo "ERROR: id3v2 version mismatch: installed ${INSTALLED_ID3V2}, expected ${PINNED_ID3V2}"
  VERSION_MISMATCH=1
fi

if ! check_version_match "bwfmetaedit" "$INSTALLED_BWFMETAEDIT" "$PINNED_BWFMETAEDIT"; then
  echo "ERROR: bwfmetaedit version mismatch: installed ${INSTALLED_BWFMETAEDIT}, expected ${PINNED_BWFMETAEDIT}"
  VERSION_MISMATCH=1
fi

if ! check_version_match "exiftool" "$INSTALLED_EXIFTOOL" "$PINNED_EXIFTOOL"; then
  echo "ERROR: exiftool version mismatch: installed ${INSTALLED_EXIFTOOL}, expected ${PINNED_EXIFTOOL}"
  VERSION_MISMATCH=1
fi

if [ -z "$INSTALLED_LIBSNDFILE" ]; then
  echo "ERROR: libsndfile not installed (required by soundfile Python package)"
  VERSION_MISMATCH=1
elif [ "$INSTALLED_LIBSNDFILE" != "installed" ] && ! check_version_match "libsndfile" "$INSTALLED_LIBSNDFILE" "$PINNED_LIBSNDFILE"; then
  echo "WARNING: libsndfile version mismatch: installed ${INSTALLED_LIBSNDFILE}, expected ${PINNED_LIBSNDFILE}"
  echo "Continuing as library version may still be compatible..."
fi

if [ "$VERSION_MISMATCH" -eq 1 ]; then
  echo ""
  echo "ERROR: Version verification failed. Installed versions don't match pinned versions."
  exit 1
fi

echo "All installed versions match pinned versions."

echo ""
echo "Verifying libsndfile library is accessible (required by soundfile Python package)..."
# Check if libsndfile library file exists and is accessible
LIBSNDFILE_LIB="${HOMEBREW_PREFIX}/lib/libsndfile.dylib"
if [ ! -f "$LIBSNDFILE_LIB" ]; then
  echo "ERROR: libsndfile library not found at expected location: $LIBSNDFILE_LIB"
  echo ""
  echo "This indicates libsndfile installation may have failed."
  echo "Verify installation: brew list libsndfile"
  exit 1
fi

# Ensure Homebrew lib directory is in library search path for Python
# This is critical for Python to find libsndfile when soundfile imports it
export DYLD_LIBRARY_PATH="${HOMEBREW_PREFIX}/lib:${DYLD_LIBRARY_PATH:-}"
export PKG_CONFIG_PATH="${HOMEBREW_PREFIX}/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
if [ -n "$GITHUB_ENV" ]; then
  echo "DYLD_LIBRARY_PATH=${HOMEBREW_PREFIX}/lib:${DYLD_LIBRARY_PATH:-}" >> "$GITHUB_ENV"
  echo "PKG_CONFIG_PATH=${HOMEBREW_PREFIX}/lib/pkgconfig:${PKG_CONFIG_PATH:-}" >> "$GITHUB_ENV"
fi

# Verify pkg-config can find libsndfile (optional - soundfile is prebuilt, but useful for diagnostics)
# Check if .pc file exists first
LIBSNDFILE_PC="${HOMEBREW_PREFIX}/lib/pkgconfig/sndfile.pc"
if [ -f "$LIBSNDFILE_PC" ]; then
  if pkg-config --exists libsndfile 2>/dev/null; then
    echo "  pkg-config can find libsndfile"
  else
    echo "WARNING: pkg-config file exists but pkg-config cannot find libsndfile."
    echo "This is not critical (soundfile is prebuilt), but may indicate configuration issues."
    echo "PKG_CONFIG_PATH: $PKG_CONFIG_PATH"
  fi
else
  echo "  Note: pkg-config file not found (not critical - soundfile is prebuilt)"
fi

# Try to import soundfile if available (it may be installed as part of Python dependencies)
if python3 -c "import soundfile" 2>/dev/null; then
  echo "  libsndfile is accessible to Python (soundfile import successful)"
else
  # Check if soundfile is installed but can't import (this is an error)
  # Use importlib to check if soundfile module exists
  SOUNDFILE_CHECK=$(python3 -c "
import sys
try:
    import importlib.util
    spec = importlib.util.find_spec('soundfile')
    if spec is not None:
        sys.exit(0)
    else:
        sys.exit(1)
except Exception:
    sys.exit(1)
" 2>/dev/null; echo $?)

  if [ "$SOUNDFILE_CHECK" -eq 0 ]; then
    echo "ERROR: soundfile Python package is installed but cannot import libsndfile."
    echo "The soundfile package cannot load libsndfile library."
    echo ""
    echo "Library location: $LIBSNDFILE_LIB"
    echo ""
    echo "This usually happens when:"
    echo "  1. libsndfile is installed but not in the library search path"
    echo "  2. Python was installed before libsndfile"
    echo ""
    echo "To fix:"
    echo "  1. Reinstall soundfile: pip install --force-reinstall soundfile"
    echo "  2. Or set DYLD_LIBRARY_PATH: export DYLD_LIBRARY_PATH=\"${HOMEBREW_PREFIX}/lib:\$DYLD_LIBRARY_PATH\""
    exit 1
  else
    # soundfile not installed yet, but verify library file exists and is loadable
    # This check MUST pass or installation should fail
    # Try loading without DYLD_LIBRARY_PATH first (Homebrew libs should be findable)
    # Then try with DYLD_LIBRARY_PATH as fallback
    LIB_LOADABLE=0
    if python3 -c "import ctypes; ctypes.CDLL('$LIBSNDFILE_LIB')" 2>/dev/null; then
      echo "  libsndfile library found and loadable at: $LIBSNDFILE_LIB"
      LIB_LOADABLE=1
    elif DYLD_LIBRARY_PATH="${HOMEBREW_PREFIX}/lib:${DYLD_LIBRARY_PATH:-}" python3 -c "import ctypes; ctypes.CDLL('$LIBSNDFILE_LIB')" 2>/dev/null; then
      echo "  libsndfile library found and loadable at: $LIBSNDFILE_LIB (with DYLD_LIBRARY_PATH)"
      LIB_LOADABLE=1
    fi

    if [ "$LIB_LOADABLE" -eq 0 ]; then
      echo "ERROR: libsndfile library found but cannot be loaded by Python."
      echo "Library location: $LIBSNDFILE_LIB"
      echo ""
      echo "This indicates libsndfile installation is incomplete or inaccessible to Python."
      echo "The library file exists but Python cannot load it, which will cause"
      echo "soundfile import to fail when Python dependencies are installed."
      echo ""
      echo "Possible causes:"
      echo "  1. Library file is corrupted or incomplete"
      echo "  2. Library dependencies are missing"
      echo "  3. Library path is not accessible to Python"
      echo ""
      echo "Verification:"
      echo "  - Library file exists: $([ -f "$LIBSNDFILE_LIB" ] && echo "YES" || echo "NO")"
      echo "  - Library is readable: $([ -r "$LIBSNDFILE_LIB" ] && echo "YES" || echo "NO")"
      echo "  - Homebrew prefix: $HOMEBREW_PREFIX"
      echo ""
      echo "Debugging:"
      echo "  - Check library dependencies: otool -L $LIBSNDFILE_LIB"
      echo "  - Check library info: file $LIBSNDFILE_LIB"
      echo ""
      echo "Try:"
      echo "  1. Reinstall libsndfile: brew reinstall libsndfile"
      echo "  2. Check if library dependencies are installed"
      exit 1
    fi
  fi
fi

echo ""
echo "Verifying installed tools are available in PATH..."
MISSING_TOOLS=()
TOOLS_TO_LINK=()

# Check each tool, including ffprobe which comes from ffmpeg@7 (keg-only)
for tool in ffprobe flac metaflac mediainfo id3v2 exiftool; do
  if ! command -v "$tool" &>/dev/null; then
    # Check if tool is installed via Homebrew but not linked
    BREW_PACKAGE=""
    case "$tool" in
      ffprobe|ffmpeg)
        BREW_PACKAGE="ffmpeg@${PINNED_FFMPEG}"
        ;;
      flac|metaflac)
        BREW_PACKAGE="flac"
        ;;
      mediainfo)
        BREW_PACKAGE="media-info"
        ;;
      id3v2)
        BREW_PACKAGE="id3v2"
        ;;
      exiftool)
        BREW_PACKAGE="exiftool"
        ;;
    esac

    if [ -n "$BREW_PACKAGE" ] && brew list "$BREW_PACKAGE" &>/dev/null 2>&1; then
      # Tool is installed but not in PATH - needs to be linked
      TOOLS_TO_LINK+=("$tool:$BREW_PACKAGE")
    else
      # Tool is not installed at all
      MISSING_TOOLS+=("$tool")
    fi
  fi
done

if [ ${#TOOLS_TO_LINK[@]} -ne 0 ]; then
  echo ""
  echo "The following tools are installed but not available in PATH:"
  printf '  - %s\n' "${TOOLS_TO_LINK[@]%%:*}"
  echo ""
  echo "Attempting to link packages..."

  LINK_FAILED=0
  for tool_info in "${TOOLS_TO_LINK[@]}"; do
    tool="${tool_info%%:*}"
    brew_package="${tool_info##*:}"

    if [ "$tool" = "ffprobe" ] || [ "$tool" = "ffmpeg" ]; then
      # ffmpeg@7 is keg-only, cannot be linked - add to PATH instead
      FFMPEG_BIN_PATH="${HOMEBREW_PREFIX}/opt/ffmpeg@${PINNED_FFMPEG}/bin"
      if [ -d "$FFMPEG_BIN_PATH" ]; then
        export PATH="$FFMPEG_BIN_PATH:$PATH"
        echo "  ✓ Added ffmpeg@${PINNED_FFMPEG} to PATH (keg-only package)"
      fi
    else
      # Try to link the package
      echo "  Linking $brew_package..."
      if brew link "$brew_package" 2>&1 | grep -v "Warning\|Linking\|already symlinked"; then
        # Check if linking was successful
        if command -v "$tool" &>/dev/null; then
          echo "  ✓ $tool is now available in PATH"
        else
          echo "  ✗ Failed to link $brew_package"
          LINK_FAILED=1
        fi
      else
        # brew link succeeded (warnings are normal)
        if command -v "$tool" &>/dev/null; then
          echo "  ✓ $tool is now available in PATH"
        else
          echo "  ✗ $tool still not in PATH after linking"
          LINK_FAILED=1
        fi
      fi
    fi
  done

  # Re-check if all tools are now available
  STILL_MISSING=()
  for tool_info in "${TOOLS_TO_LINK[@]}"; do
    tool="${tool_info%%:*}"
    if ! command -v "$tool" &>/dev/null; then
      STILL_MISSING+=("$tool")
    fi
  done

  if [ ${#STILL_MISSING[@]} -ne 0 ]; then
    echo ""
    echo "Some tools are still not available in PATH:"
    printf '  - %s\n' "${STILL_MISSING[@]}"
    echo ""
    echo "To fix manually, run these commands:"
    for tool_info in "${TOOLS_TO_LINK[@]}"; do
      tool="${tool_info%%:*}"
      brew_package="${tool_info##*:}"
      if [ "$tool" = "ffprobe" ] || [ "$tool" = "ffmpeg" ]; then
        echo "  export PATH=\"${HOMEBREW_PREFIX}/opt/ffmpeg@${PINNED_FFMPEG}/bin:\$PATH\""
      else
        echo "  brew link $brew_package"
      fi
    done
    exit 1
  fi
fi

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
  echo "ERROR: The following tools are not installed:"
  printf '  - %s\n' "${MISSING_TOOLS[@]}"
  echo ""
  echo "Installation may have failed. Check the output above for errors."
  exit 1
fi

echo "All system dependencies installed successfully!"

# Automatically add PATH setup to shell profile for local development
if [ -z "$GITHUB_PATH" ] && [ -z "$CI" ]; then
  # Detect shell and determine profile file
  SHELL_PROFILE=""
  if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ] || [ "$SHELL" = "/opt/homebrew/bin/zsh" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
  elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ] || [ "$SHELL" = "/usr/bin/bash" ]; then
    SHELL_PROFILE="$HOME/.bash_profile"
    # Fallback to .bashrc if .bash_profile doesn't exist
    if [ ! -f "$SHELL_PROFILE" ] && [ -f "$HOME/.bashrc" ]; then
      SHELL_PROFILE="$HOME/.bashrc"
    fi
  fi

  if [ -n "$SHELL_PROFILE" ]; then
    # Marker to identify our PATH additions
    MARKER="# audiometa-python: system dependencies PATH"

    # Check if already added
    if grep -q "$MARKER" "$SHELL_PROFILE" 2>/dev/null; then
      echo ""
      echo "PATH setup already exists in $SHELL_PROFILE"
      echo "To update it, remove the existing section and re-run this script."
    else
      echo ""
      echo "Adding PATH setup to $SHELL_PROFILE..."

      # Collect PATH exports
      PATH_EXPORTS=()
      if [ -n "$HOMEBREW_BIN" ] && [ -d "$HOMEBREW_BIN" ]; then
        PATH_EXPORTS+=("export PATH=\"${HOMEBREW_BIN}:\$PATH\"")
      fi
      if [ -n "$FFMPEG_BIN_PATH" ] && [ -d "$FFMPEG_BIN_PATH" ]; then
        PATH_EXPORTS+=("export PATH=\"${FFMPEG_BIN_PATH}:\$PATH\"")
      fi
      for opt_package in flac; do
        OPT_BIN="${HOMEBREW_PREFIX}/opt/${opt_package}/bin"
        if [ -d "$OPT_BIN" ]; then
          PATH_EXPORTS+=("export PATH=\"${OPT_BIN}:\$PATH\"")
        fi
      done
      if [ -n "$PINNED_FLAC" ]; then
        FLAC_CELLAR_BIN="${HOMEBREW_PREFIX}/Cellar/flac/${PINNED_FLAC}/bin"
        if [ -d "$FLAC_CELLAR_BIN" ]; then
          PATH_EXPORTS+=("export PATH=\"${FLAC_CELLAR_BIN}:\$PATH\"")
        fi
      fi

      if [ ${#PATH_EXPORTS[@]} -gt 0 ]; then
        {
          echo ""
          echo "$MARKER"
          printf '%s\n' "${PATH_EXPORTS[@]}"
        } >> "$SHELL_PROFILE"
        echo "✓ Added PATH setup to $SHELL_PROFILE"
        echo "  Run 'source $SHELL_PROFILE' or open a new terminal to apply changes."
      fi
    fi
  else
    echo ""
    echo "Could not detect shell profile. Please manually add these lines to your shell profile:"
    if [ -n "$HOMEBREW_BIN" ] && [ -d "$HOMEBREW_BIN" ]; then
      echo "  export PATH=\"${HOMEBREW_BIN}:\$PATH\""
    fi
    if [ -n "$FFMPEG_BIN_PATH" ] && [ -d "$FFMPEG_BIN_PATH" ]; then
      echo "  export PATH=\"${FFMPEG_BIN_PATH}:\$PATH\""
    fi
    for opt_package in flac; do
      OPT_BIN="${HOMEBREW_PREFIX}/opt/${opt_package}/bin"
      if [ -d "$OPT_BIN" ]; then
        echo "  export PATH=\"${OPT_BIN}:\$PATH\""
      fi
    done
    if [ -n "$PINNED_FLAC" ]; then
      FLAC_CELLAR_BIN="${HOMEBREW_PREFIX}/Cellar/flac/${PINNED_FLAC}/bin"
      if [ -d "$FLAC_CELLAR_BIN" ]; then
        echo "  export PATH=\"${FLAC_CELLAR_BIN}:\$PATH\""
      fi
    fi
  fi
fi
