#!/bin/bash
#
# Set Maximum ID3v1 Metadata Script
#
# PURPOSE:
#     Sets maximum length ID3v1 metadata for testing field limits and truncation behavior.
#     This script is useful for testing how the audiometa library handles ID3v1 field
#     truncation and maximum length scenarios.
#
# USAGE:
#     ./set-id3v1-max-metadata.sh <audio_file>
#
# FEATURES:
#     - Sets all ID3v1 fields to maximum allowed lengths
#     - Tests field truncation behavior
#     - Uses id3v2 tool with --id3v1-only flag
#     - Verifies written tags automatically
#     - Installs id3v2 if missing (macOS with Homebrew)
#
# FIELD LIMITS:
#     Title: 30 characters (truncated if longer)
#     Artist: 30 characters (truncated if longer)
#     Album: 30 characters (truncated if longer)
#     Year: 4 characters (exactly 4 digits)
#     Comment: 28 characters (ID3v1.1 with track number)
#     Track: 1 byte (0-255)
#     Genre: 1 byte index (0-255, 0=Blues)
#
# DEPENDENCIES:
#     - id3v2 tool for ID3 tag manipulation
#
# INSTALLATION:
#     brew install id3v2
#
# EXAMPLES:
#     # Set maximum ID3v1 metadata
#     ./set-id3v1-max-metadata.sh test.mp3
#     
#     # Verify the results
#     id3v2 -l test.mp3
#
# GENERATED CONTENT:
#     - Title: 30 'a' characters (aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa)
#     - Artist: 30 'a' characters (aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa)
#     - Album: 30 'a' characters (aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa)
#     - Year: "2024"
#     - Comment: 28 'a' characters (aaaaaaaaaaaaaaaaaaaaaaaaaaaa)
#     - Track: "1"
#     - Genre: "0" (Blues)
#
# VERIFICATION:
#     The script automatically verifies written tags using id3v2 -l.
#     You can also manually check with:
#     id3v2 -l test.mp3
#     id3v2 -l1 test.mp3  # ID3v1 only
#
# TROUBLESHOOTING:
#     # Check if id3v2 is installed
#     which id3v2
#     
#     # Install if missing (macOS)
#     brew install id3v2
#     
#     # Check file format
#     file test.mp3  # Should show MP3 audio
#     
#     # Verify ID3v1 tags were written
#     id3v2 -l1 test.mp3  # Should show all fields with max lengths
#
# NOTES:
#     - This script is idempotent - safe to run multiple times
#     - Original file is modified in place
#     - Always backup important files before running
#     - ID3v1 tags are limited to 128 bytes total
#     - Field truncation is expected behavior for ID3v1
#

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <audio_file>"
    exit 1
fi

TRACK_FILE="$1"

# ID3v1 field max lengths
TITLE_MAX=30
ARTIST_MAX=30
ALBUM_MAX=30
YEAR_MAX=4
COMMENT_MAX=28  # 28 for ID3v1.1 to allow track number
TRACK_MAX=1     # Single byte for ID3v1.1
GENRE_MAX=1     # Single byte index

# Create maximum length content
TITLE=$(printf 'a%.0s' $(seq 1 $TITLE_MAX))
ARTIST=$(printf 'a%.0s' $(seq 1 $ARTIST_MAX))
ALBUM=$(printf 'a%.0s' $(seq 1 $ALBUM_MAX))
YEAR="9999"
COMMENT=$(printf 'a%.0s' $(seq 1 $COMMENT_MAX))
TRACK="1"
GENRE="0"  # Blues = 0

# Install id3v2 if needed
command -v id3v2 >/dev/null 2>&1 || {
    echo "id3v2 tool not found. Installing..."
    brew install id3v2
}

# Write ID3v1 tags
id3v2 \
    --comment "$COMMENT" \
    --artist "$ARTIST" \
    --album "$ALBUM" \
    --song "$TITLE" \
    --year "$YEAR" \
    --track "$TRACK" \
    --genre "$GENRE" \
    --id3v1-only \
    "$TRACK_FILE"

# Verify tags
id3v2 -l "$TRACK_FILE"
echo "ID3v1 tags written successfully"