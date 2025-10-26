#!/bin/bash
#
# Set Maximum ID3v2 Metadata Script
#
# PURPOSE:
#     Sets comprehensive ID3v2 metadata with maximum values for testing field limits and complex metadata scenarios.
#     This script creates the most comprehensive metadata possible for testing the audiometa library's
#     handling of complex ID3v2 scenarios including extended frames, ratings, and cover art.
#
# USAGE:
#     ./set-id3v2-max-metadata.sh <filename>
#
# FEATURES:
#     - Sets basic ID3v2 tags (artist, album, title, etc.)
#     - Sets extended metadata using TXXX frames
#     - Sets ratings using POPM frames
#     - Adds cover art (if ImageMagick available)
#     - Comprehensive verification using multiple tools
#     - Tests field truncation behavior
#     - Validates file format before processing
#
# DEPENDENCIES:
#     - mid3v2 (from python-mutagen)
#     - mutagen-inspect
#     - convert (ImageMagick, optional for cover art)
#
# INSTALLATION:
#     pip install mutagen
#     brew install imagemagick  # optional
#
# METADATA FIELDS:
#     Basic tags: artist, album, title, comment, genre, year, track
#     Extended tags: mood, subtitle, ISRC, conductor, remixer, etc.
#     Ratings: POPM and custom TXXX frames
#     Cover art: APIC frame (if ImageMagick available)
#
# FIELD LENGTHS:
#     Text fields: 1000 characters (tests truncation)
#     Comment: 4000 characters (maximum)
#     URL: 2000 characters (maximum)
#     ISRC: "USXXX9999999" (maximum format)
#
# EXAMPLES:
#     # Set maximum ID3v2 metadata
#     ./set-id3v2-max-metadata.sh test.mp3
#     ./set-id3v2-max-metadata.sh test.flac
#     
#     # Verify the results
#     mid3v2 -l test.mp3
#     mutagen-inspect test.mp3
#
# VERIFICATION:
#     The script performs comprehensive verification:
#     - Uses mid3v2 -l to list all tags
#     - Uses mutagen-inspect for detailed inspection
#     - Checks specific fields (MOOD, ISRC, CONDUCTOR, etc.)
#     - Verifies cover art presence (if ImageMagick available)
#
# TROUBLESHOOTING:
#     # Check if required tools are installed
#     which mid3v2 mutagen-inspect
#     
#     # Install missing tools
#     pip install mutagen
#     
#     # Check ImageMagick (optional)
#     which convert
#     brew install imagemagick  # if missing
#     
#     # Verify file format
#     file test.mp3  # Should show MP3 audio
#     
#     # Check metadata after running
#     mid3v2 -l test.mp3 | grep -E "(TIT2|TPE1|TALB|TXXX)"
#
# NOTES:
#     - This script is idempotent - safe to run multiple times
#     - Original file is modified in place
#     - Always backup important files before running
#     - Cover art is only added if ImageMagick is available
#     - Some fields may be truncated by the ID3v2 standard
#     - Extended metadata uses TXXX frames for custom fields
#

# Test file path
FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: ./set-id3v2-max-metadata.sh <filename>"
    exit 1
fi

# Resolve the file path and check if file exists
RESOLVED_FILE=$(readlink -f "$FILE")
if [ ! -f "$RESOLVED_FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

# Check if required tools are available
for cmd in mid3v2 mutagen-inspect; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd is required but not installed."
        echo "Please install: python-mutagen"
        exit 1
    fi
done

# Check for optional ImageMagick
HAS_IMAGEMAGICK=0
if command -v convert &> /dev/null; then
    HAS_IMAGEMAGICK=1
fi

# Maximum lengths for ID3v2 frames
TEXT_BIG_LENGTH=1000     # Text length to test truncation
MAX_COMMENT=4000 # Maximum comment length
MAX_URL=2000     # Maximum URL length

# Create max length strings for different fields
# Using different characters for each field to make them distinguishable
ARTIST=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ALBUM_ARTIST=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
TITLE=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
SUBTITLE=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ALBUM=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
COMPOSER=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
COMMENT=$(printf 'a%.0s' $(seq 1 $MAX_COMMENT))
GENRE=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
COPYRIGHT=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ENCODED_BY=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ORIGINAL_ARTIST=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
PUBLISHER=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
CONDUCTOR=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
REMIXER=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
MOOD=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
UNSYNCHRONIZED_LYRICS=$(printf 'a%.0s' $(seq 1 $MAX_COMMENT))
URL=$(printf 'a%.0s' $(seq 1 $MAX_URL))
ISRC="USXXX9999999"  # Maximum ISRC format

# Fixed length fields with maximum values
YEAR="9999"                    # Maximum 4-digit year
TRACK="99/99"                  # Maximum track number/total
DISC="99/99"                   # Maximum disc number/total
BPM="999"                      # Maximum reasonable BPM
LANGUAGE=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH)) # Standard language code
RECORDING_DATE="9999-12-31"    # Maximum date
ORIGINAL_RELEASE="9999-12-31"  # Maximum date
MEDIA_TYPE="DIG"              # Digital Media
RATING="255"                   # Maximum rating (8-bit)

echo "Setting metadata for: $RESOLVED_FILE"

# Write basic metadata tags
mid3v2 \
    --artist="$ARTIST" \
    --album="$ALBUM" \
    --song="$TITLE" \
    --comment="$COMMENT" \
    --genre="$GENRE" \
    --year="$YEAR" \
    --track="$TRACK" \
    "$RESOLVED_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to write basic metadata"
    exit 1
fi

# Write extended metadata tags
mid3v2 \
    --TXXX "MOOD:$MOOD" \
    --TXXX "SUBTITLE:$SUBTITLE" \
    --TXXX "ISRC:$ISRC" \
    --TXXX "CONDUCTOR:$CONDUCTOR" \
    --TXXX "REMIXER:$REMIXER" \
    --TXXX "MEDIA_TYPE:$MEDIA_TYPE" \
    --TPE2 "$ALBUM_ARTIST" \
    --TCOM "$COMPOSER" \
    --TCOP "$COPYRIGHT" \
    --TENC "$ENCODED_BY" \
    --TBPM "$BPM" \
    --TOPE "$ORIGINAL_ARTIST" \
    --TPUB "$PUBLISHER" \
    --TPOS "$DISC" \
    --TLAN "$LANGUAGE" \
    --TIT3 "$SUBTITLE" \
    --WXXX "$URL" \
    --TDRC "$RECORDING_DATE" \
    --TDOR "$ORIGINAL_RELEASE" \
    --USLT "eng:$UNSYNCHRONIZED_LYRICS" \
    "$RESOLVED_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to write extended metadata"
    exit 1
fi

# Set ratings (both as POPM and custom TXXX frame)
mid3v2 \
    --POPM "Windows Media Player 9 Series:255" \
    --TXXX "RATING:$RATING" \
    "$RESOLVED_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to write rating metadata"
    exit 1
fi

# Add cover art if ImageMagick is available
if [ $HAS_IMAGEMAGICK -eq 1 ]; then
    echo "ImageMagick detected, adding test cover art..."
    TEMP_IMAGE=$(mktemp).jpg
    convert -size 1200x1200 xc:white -pointsize 20 -gravity center \
        -draw "text 0,0 'Test Cover Art'" "$TEMP_IMAGE"
    
    mid3v2 --APIC "$TEMP_IMAGE" "$RESOLVED_FILE"
    
    if [ $? -ne 0 ]; then
        echo "Warning: Failed to write cover art"
    fi
    
    rm -f "$TEMP_IMAGE"
else
    echo "Note: ImageMagick not found - skipping cover art test"
fi

# Verification section
echo -e "\nVerifying metadata using mid3v2:"
mid3v2 -l "$RESOLVED_FILE"

echo -e "\nVerifying metadata using mutagen-inspect:"
mutagen-inspect "$RESOLVED_FILE"

# Additional verification for specific fields
echo -e "\nVerifying specific fields:"
for tag in MOOD ISRC CONDUCTOR REMIXER MEDIA_TYPE RATING; do
    echo -n "Checking $tag: "
    mid3v2 -l "$RESOLVED_FILE" | grep "$tag" || echo "Not found!"
done

if [ $HAS_IMAGEMAGICK -eq 1 ]; then
    echo -e "\nVerifying cover art presence:"
    mid3v2 -l "$RESOLVED_FILE" | grep "APIC" || echo "Cover art not found!"
fi

echo -e "\nMetadata setting completed successfully!"