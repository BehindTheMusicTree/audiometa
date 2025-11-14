#!/bin/bash
# Setup script for system dependencies
# Ensures local environment matches CI configuration
# Reads from system-dependencies.toml

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$REPO_ROOT/system-dependencies.toml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            echo "ubuntu"
        else
            echo "unknown-linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Install dependencies for Ubuntu
install_ubuntu() {
    echo -e "${BLUE}Installing system dependencies for Ubuntu...${NC}"

    echo -e "${YELLOW}Updating package lists...${NC}"
    sudo apt-get update

    echo -e "${YELLOW}Installing pinned package versions from Ubuntu repos...${NC}"
    # Load pinned versions from system-dependencies.toml
    eval "$(python3 "${SCRIPT_DIR}/ci/load-system-dependency-versions.py" bash)"

    # Verify versions are available before installing
    if ! apt-cache show ffmpeg="$PINNED_FFMPEG" &>/dev/null; then
        echo -e "${RED}✗ ERROR: Pinned ffmpeg version $PINNED_FFMPEG not available${NC}"
        echo "Available versions:"
        apt-cache madison ffmpeg | head -5
        exit 1
    fi

    if ! apt-cache show flac="$PINNED_FLAC" &>/dev/null; then
        echo -e "${RED}✗ ERROR: Pinned flac version $PINNED_FLAC not available${NC}"
        echo "Available versions:"
        apt-cache madison flac | head -5
        exit 1
    fi

    if ! apt-cache show mediainfo="$PINNED_MEDIAINFO" &>/dev/null; then
        echo -e "${RED}✗ ERROR: Pinned mediainfo version $PINNED_MEDIAINFO not available${NC}"
        echo "Available versions:"
        apt-cache madison mediainfo | head -5
        exit 1
    fi

    if ! apt-cache show id3v2="$PINNED_ID3V2" &>/dev/null; then
        echo -e "${RED}✗ ERROR: Pinned id3v2 version $PINNED_ID3V2 not available${NC}"
        echo "Available versions:"
        apt-cache madison id3v2 | head -5
        exit 1
    fi

    sudo apt-get install -y ffmpeg="$PINNED_FFMPEG" flac="$PINNED_FLAC" mediainfo="$PINNED_MEDIAINFO" id3v2="$PINNED_ID3V2"

    echo -e "${YELLOW}Installing bwfmetaedit...${NC}"
    # Try installing from Ubuntu repos first
    if sudo apt-get install -y bwfmetaedit 2>/dev/null; then
        echo -e "${GREEN}✓ bwfmetaedit installed from Ubuntu repos${NC}"
    else
        # If not in repos, download from MediaArea
        UBUNTU_VERSION=$(grep VERSION_ID /etc/os-release | cut -d'"' -f2 | cut -d. -f1,2)
        echo "Detected Ubuntu version: ${UBUNTU_VERSION}"

        # Pinned version from system-dependencies.toml
        # Must be available, no fallback - fails if not found
        PINNED_VERSION="${PINNED_BWFMETAEDIT}"
        URL="https://mediaarea.net/download/binary/bwfmetaedit/${PINNED_VERSION}/bwfmetaedit_${PINNED_VERSION}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb"

        if ! wget -q --spider "$URL" 2>/dev/null; then
          echo -e "${RED}✗ ERROR: Pinned bwfmetaedit version ${PINNED_VERSION} not available for Ubuntu ${UBUNTU_VERSION}${NC}"
          echo "URL: $URL"
          exit 1
        fi

        echo "Installing pinned bwfmetaedit version ${PINNED_VERSION} for Ubuntu ${UBUNTU_VERSION}"
        wget "$URL"
        sudo dpkg -i bwfmetaedit_${PINNED_VERSION}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb || sudo apt-get install -f -y
        rm bwfmetaedit_${PINNED_VERSION}-1_amd64.xUbuntu_${UBUNTU_VERSION}.deb
        echo -e "${GREEN}✓ bwfmetaedit installed${NC}"
    fi
}

# Install dependencies for macOS
install_macos() {
    echo -e "${BLUE}Installing system dependencies for macOS...${NC}"

    if ! command -v brew &> /dev/null; then
        echo -e "${RED}✗ Homebrew not found. Please install Homebrew first:${NC}"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi

    echo -e "${YELLOW}Installing pinned package versions via Homebrew...${NC}"
    # Load pinned versions from system-dependencies.toml
    eval "$(python3 "${SCRIPT_DIR}/ci/load-system-dependency-versions.py" bash)"

    # Homebrew version pinning format: brew install package@version
    brew install \
      ffmpeg@${PINNED_FFMPEG} \
      flac@${PINNED_FLAC} \
      mediainfo@${PINNED_MEDIAINFO} \
      bwfmetaedit@${PINNED_BWFMETAEDIT} \
      id3v2@${PINNED_ID3V2} || {
      echo -e "${RED}✗ ERROR: Pinned versions not available.${NC}"
      echo "Update system-dependencies.toml with correct versions."
      echo "Check available versions with: brew info <package>"
      exit 1
    }

    echo -e "${GREEN}✓ All packages installed${NC}"
}

# Print instructions for Windows
install_windows() {
    echo -e "${BLUE}Windows installation instructions:${NC}"
    echo ""
    echo "1. Install Chocolatey if not already installed:"
    echo "   https://chocolatey.org/install"
    echo ""
    echo "2. Run the installation script in PowerShell (as Administrator):"
    echo "   .\\scripts\\ci\\install-system-dependencies-windows.ps1"
    echo ""
    echo "This installs all system dependencies including bwfmetaedit (pinned version)."
    echo "Or see .github/workflows/ci.yml for the complete Windows installation steps."
}

# Verify installation
verify_installation() {
    echo -e "${BLUE}Verifying installation...${NC}"

    OS=$(detect_os)

    if [ "$OS" = "ubuntu" ] || [ "$OS" = "macos" ]; then
        echo ""
        echo -e "${YELLOW}Checking tools:${NC}"
        ffprobe -version 2>/dev/null && echo -e "${GREEN}✓ ffprobe${NC}" || echo -e "${RED}✗ ffprobe not found${NC}"
        flac --version 2>/dev/null && echo -e "${GREEN}✓ flac${NC}" || echo -e "${RED}✗ flac not found${NC}"
        metaflac --version 2>/dev/null && echo -e "${GREEN}✓ metaflac${NC}" || echo -e "${YELLOW}⚠ metaflac not found (should be bundled with flac)${NC}"
        mediainfo --version 2>/dev/null && echo -e "${GREEN}✓ mediainfo${NC}" || echo -e "${RED}✗ mediainfo not found${NC}"
        bwfmetaedit --version 2>/dev/null && echo -e "${GREEN}✓ bwfmetaedit${NC}" || echo -e "${RED}✗ bwfmetaedit not found${NC}"
        id3v2 --version 2>/dev/null && echo -e "${GREEN}✓ id3v2${NC}" || echo -e "${RED}✗ id3v2 not found${NC}"
        if command -v mid3v2 &> /dev/null; then
            mid3v2 --version 2>/dev/null && echo -e "${GREEN}✓ mid3v2${NC}" || echo -e "${YELLOW}⚠ mid3v2 not found (mutagen provides it, may not be in PATH)${NC}"
        else
            echo -e "${YELLOW}⚠ mid3v2 not found (mutagen provides it, may not be in PATH)${NC}"
        fi
    fi
}

# Main
main() {
    echo -e "${BLUE}=== System Dependencies Setup ===${NC}"
    echo ""

    OS=$(detect_os)
    echo -e "Detected OS: ${YELLOW}$OS${NC}"
    echo ""

    case "$OS" in
        ubuntu)
            install_ubuntu
            ;;
        macos)
            install_macos
            ;;
        windows)
            install_windows
            exit 0
            ;;
        *)
            echo -e "${RED}✗ Unsupported OS: $OS${NC}"
            echo "Please install dependencies manually. See system-dependencies.toml for requirements."
            exit 1
            ;;
    esac

    echo ""
    verify_installation

    echo ""
    echo -e "${GREEN}✓ System dependencies setup complete!${NC}"
    echo ""
    echo "Configuration file: $CONFIG_FILE"
    echo "This ensures your local environment matches CI."
}

main


