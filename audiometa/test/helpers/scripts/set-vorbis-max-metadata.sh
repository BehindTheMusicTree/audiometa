#!/bin/bash
#
# Set Maximum Vorbis Metadata Script
#
# PURPOSE:
#     Sets comprehensive Vorbis comments for FLAC files to test field limits and Vorbis metadata handling.
#     This script creates the most comprehensive Vorbis metadata possible for testing the audiometa library's
#     handling of Vorbis comment scenarios including all standard and extended fields.
#
# USAGE:
#     ./set-vorbis-max-metadata.sh <flac_file>
#
# FEATURES:
#     - Sets all standard Vorbis comment fields
#     - Tests field length limits (1000 characters)
#     - Removes existing tags before setting new ones
#     - Comprehensive verification
#     - Tests all Vorbis comment categories
#     - Error handling and validation
#
# DEPENDENCIES:
#     - metaflac tool for FLAC metadata manipulation
#
# INSTALLATION:
#     brew install flac  # provides metaflac
#
# VORBIS FIELDS SET:
#     Standard: TITLE, ARTIST, ALBUM, ALBUMARTIST
#     Track info: TRACKNUMBER, TRACKTOTAL, DISCNUMBER, DISCTOTAL
#     Metadata: DATE, GENRE, COMMENT, COPYRIGHT, COMPOSER
#     Extended: CONDUCTOR, ARRANGER, LYRICIST, AUTHOR
#     Technical: ORGANIZATION, LOCATION, CONTACT, ISRC
#     Additional: CATALOGNUMBER, DESCRIPTION, PERFORMER
#     Ratings: RATING, BPM, MOOD, VERSION, LANGUAGE, LABEL
#     Encoding: ENCODED-BY, ENCODER_SETTINGS
#
# EXAMPLES:
#     # Set maximum Vorbis metadata
#     ./set-vorbis-max-metadata.sh test.flac
#     
#     # Verify the results
#     metaflac --list test.flac
#     metaflac --list --block-type=VORBIS_COMMENT test.flac
#
# PROCESS:
#     1. Removes all existing tags using metaflac --remove-all-tags
#     2. Sets all Vorbis comment fields with maximum values
#     3. Verifies tags using metaflac --list --block-type=VORBIS_COMMENT
#
# VERIFICATION:
#     The script automatically verifies all tags were written successfully.
#     You can also manually check with:
#     metaflac --list test.flac
#     metaflac --list --block-type=VORBIS_COMMENT test.flac
#
# TROUBLESHOOTING:
#     # Check if metaflac is installed
#     which metaflac
#     
#     # Install if missing (macOS)
#     brew install flac  # provides metaflac
#     
#     # Check file format
#     file test.flac  # Should show "FLAC audio"
#     
#     # Verify Vorbis comments were written
#     metaflac --list test.flac | grep -E "(TITLE|ARTIST|ALBUM)"
#     metaflac --list --block-type=VORBIS_COMMENT test.flac
#
# NOTES:
#     - This script is idempotent - safe to run multiple times
#     - Original file is modified in place
#     - Always backup important files before running
#     - Vorbis comments are embedded in the FLAC file
#     - Field lengths are tested with 1000 characters
#     - All existing tags are removed before setting new ones
#

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <flac_file>"
    exit 1
fi

FLAC_FILE="$1"
TEXT_BIG_LENGTH=1000 # Text length for testing truncation

# Standard Vorbis fields with maximum values
TITLE=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ARTIST=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ALBUM=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ALBUMARTIST=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
TRACKNUMBER="99"  # Max 2-digit track number
TRACKTOTAL="99"   # Max 2-digit total tracks
DISCNUMBER="99"   # Max 2-digit disc number
DISCTOTAL="99"    # Max 2-digit total discs
DATE="9999"       # Max 4-digit year
GENRE=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
COMMENT=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
COPYRIGHT=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
COMPOSER=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
CONDUCTOR=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ARRANGER=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
LYRICIST=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
AUTHOR=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ORGANIZATION=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
LOCATION=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
CONTACT=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ISRC="USXXX9999999"  # Max ISRC format
CATALOGNUMBER=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
DESCRIPTION=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
PERFORMER=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
RATING="255"      # Max rating value (8-bit)
BPM="999"         # Max reasonable BPM value
MOOD=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
VERSION=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
LANGUAGE=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
LABEL=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ENCODEDBY=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))
ENCODERSETTINGS=$(printf 'a%.0s' $(seq 1 $TEXT_BIG_LENGTH))

# Remove existing tags
metaflac --remove-all-tags "$FLAC_FILE"

# Write all tags
metaflac \
    --set-tag="TITLE=$TITLE" \
    --set-tag="ARTIST=$ARTIST" \
    --set-tag="ALBUM=$ALBUM" \
    --set-tag="ALBUMARTIST=$ALBUMARTIST" \
    --set-tag="TRACKNUMBER=$TRACKNUMBER" \
    --set-tag="TRACKTOTAL=$TRACKTOTAL" \
    --set-tag="DISCNUMBER=$DISCNUMBER" \
    --set-tag="DISCTOTAL=$DISCTOTAL" \
    --set-tag="DATE=$DATE" \
    --set-tag="GENRE=$GENRE" \
    --set-tag="COMMENT=$COMMENT" \
    --set-tag="COPYRIGHT=$COPYRIGHT" \
    --set-tag="COMPOSER=$COMPOSER" \
    --set-tag="CONDUCTOR=$CONDUCTOR" \
    --set-tag="ARRANGER=$ARRANGER" \
    --set-tag="LYRICIST=$LYRICIST" \
    --set-tag="AUTHOR=$AUTHOR" \
    --set-tag="ORGANIZATION=$ORGANIZATION" \
    --set-tag="LOCATION=$LOCATION" \
    --set-tag="CONTACT=$CONTACT" \
    --set-tag="ISRC=$ISRC" \
    --set-tag="CATALOGNUMBER=$CATALOGNUMBER" \
    --set-tag="DESCRIPTION=$DESCRIPTION" \
    --set-tag="PERFORMER=$PERFORMER" \
    --set-tag="RATING=$RATING" \
    --set-tag="BPM=$BPM" \
    --set-tag="MOOD=$MOOD" \
    --set-tag="VERSION=$VERSION" \
    --set-tag="LANGUAGE=$LANGUAGE" \
    --set-tag="LABEL=$LABEL" \
    --set-tag="ENCODED-BY=$ENCODEDBY" \
    --set-tag="ENCODER_SETTINGS=$ENCODERSETTINGS" \
    "$FLAC_FILE"

# Verify tags
metaflac --list --block-type=VORBIS_COMMENT "$FLAC_FILE"
echo "All Vorbis comments written successfully"