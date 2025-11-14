#!/bin/bash
# Helper script to update pinned versions based on CI output
# Usage: After CI runs, copy the "Recommended pinned versions" output and run this script
# Or manually update system-dependencies.toml with the versions shown in CI

set -e

CONFIG_FILE="system-dependencies.toml"
WORKFLOW_FILE=".github/workflows/ci.yml"

echo "=== Update Pinned Versions ==="
echo ""
echo "This script helps update pinned versions after CI shows available versions."
echo ""
echo "Steps:"
echo "1. Run CI and check the 'Verify available package versions' step output"
echo "2. Copy the 'Recommended pinned versions' lines"
echo "3. Update $CONFIG_FILE with those versions"
echo "4. Update $WORKFLOW_FILE install command with those versions"
echo ""
echo "Or run this script interactively:"
echo ""

read -p "Enter ffmpeg version (e.g., 7:7.1.0-1ubuntu2): " FFMPEG_VERSION
read -p "Enter flac version (e.g., 1.4.3-3build1): " FLAC_VERSION
read -p "Enter mediainfo version (e.g., 24.06-1): " MEDIAINFO_VERSION
read -p "Enter id3v2 version (e.g., 0.1.12-8build2): " ID3V2_VERSION

if [ -z "$FFMPEG_VERSION" ] || [ -z "$FLAC_VERSION" ] || [ -z "$MEDIAINFO_VERSION" ] || [ -z "$ID3V2_VERSION" ]; then
    echo "Error: All versions must be provided"
    exit 1
fi

echo ""
echo "Updating $CONFIG_FILE..."
# Update config file (this is a simple example - you may need to adjust the sed pattern)
sed -i.bak "s/ffmpeg = \".*\"/ffmpeg = \"$FFMPEG_VERSION\"/" "$CONFIG_FILE"
sed -i.bak "s/flac = \".*\"/flac = \"$FLAC_VERSION\"/" "$CONFIG_FILE"
sed -i.bak "s/mediainfo = \".*\"/mediainfo = \"$MEDIAINFO_VERSION\"/" "$CONFIG_FILE"
sed -i.bak "s/id3v2 = \".*\"/id3v2 = \"$ID3V2_VERSION\"/" "$CONFIG_FILE"

echo "Updating $WORKFLOW_FILE..."
# Update workflow file install command
sed -i.bak "s/ffmpeg=[^ ]*/ffmpeg=$FFMPEG_VERSION/g" "$WORKFLOW_FILE"
sed -i.bak "s/flac=[^ ]*/flac=$FLAC_VERSION/g" "$WORKFLOW_FILE"
sed -i.bak "s/mediainfo=[^ ]*/mediainfo=$MEDIAINFO_VERSION/g" "$WORKFLOW_FILE"
sed -i.bak "s/id3v2=[^ ]*/id3v2=$ID3V2_VERSION/g" "$WORKFLOW_FILE"

echo ""
echo "Updated pinned versions:"
echo "  ffmpeg=$FFMPEG_VERSION"
echo "  flac=$FLAC_VERSION"
echo "  mediainfo=$MEDIAINFO_VERSION"
echo "  id3v2=$ID3V2_VERSION"
echo ""
echo "Backup files created: *.bak"
echo "Review changes and remove .bak files when satisfied."


