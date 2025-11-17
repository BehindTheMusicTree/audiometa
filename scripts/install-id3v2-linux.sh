#!/bin/bash
# Install id3v2 on Linux (Ubuntu/Debian) or via WSL on Windows
# Usage: install-id3v2-linux.sh <pinned_version>
# Example: install-id3v2-linux.sh "0.1.12+dfsg-7"

set -e

if [ $# -lt 1 ]; then
  echo "ERROR: Pinned version required"
  echo "Usage: $0 <pinned_version>"
  exit 1
fi

PINNED_VERSION="$1"

# Update package list
sudo apt-get update -qq

# Check if id3v2 is already installed
INSTALLED_DEB_VERSION=$(dpkg -l | grep "^ii.*id3v2" | awk '{print $3}' || echo "")

if [ -n "$INSTALLED_DEB_VERSION" ]; then
  if [ "$INSTALLED_DEB_VERSION" = "$PINNED_VERSION" ]; then
    echo "id3v2 ${INSTALLED_DEB_VERSION} already installed (matches pinned version ${PINNED_VERSION})"
    exit 0
  else
    echo "Removing existing id3v2 version ${INSTALLED_DEB_VERSION} (installing pinned version ${PINNED_VERSION})..."
    sudo apt-get remove -y id3v2 2>/dev/null || true
  fi
fi

# Install id3v2 with pinned version
echo "Installing id3v2 version ${PINNED_VERSION}..."
sudo apt-get install -y "id3v2=${PINNED_VERSION}" || {
  echo "ERROR: Failed to install id3v2 version ${PINNED_VERSION}."
  echo "This may indicate the version is no longer available."
  exit 1
}

echo "id3v2 version ${PINNED_VERSION} installed successfully"
