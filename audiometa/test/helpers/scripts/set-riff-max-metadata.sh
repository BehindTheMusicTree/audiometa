#!/bin/bash
#
# Set Maximum RIFF Metadata Script
#
# PURPOSE:
#     Sets maximum RIFF INFO metadata for WAV files to test field limits and RIFF metadata handling.
#     This script creates comprehensive RIFF metadata for testing the audiometa library's
#     handling of RIFF/WAV metadata scenarios including all standard INFO fields.
#
# USAGE:
#     ./set-riff-max-metadata.sh <wav_file>
#
# FEATURES:
#     - Sets all available RIFF INFO metadata fields
#     - Uses bwfmetaedit tool for metadata manipulation
#     - Tests field length limits (1000 characters)
#     - Validates WAV file format before processing
#     - Comprehensive field coverage
#     - Error handling and validation
#
# DEPENDENCIES:
#     - bwfmetaedit tool for RIFF metadata manipulation
#
# INSTALLATION:
#     brew install bwfmetaedit
#
# RIFF FIELDS SET:
#     INAM (Title), IART (Artist), IPRD (Album), IGNR (Genre)
#     ICRD (Date), ICMT (Comment), ISFT (Software)
#     ICOP (Copyright), IENG (Engineer), ITCH (Technician)
#     ISRC (ISRC), ISBJ (Subject), IKEY (Keywords)
#     IMED (Medium), ICMS (Commission), ITRK (Track)
#     IARL (Archival Location), ILOC (Location)
#
# EXAMPLES:
#     # Set maximum RIFF metadata
#     ./set-riff-max-metadata.sh test.wav
#     
#     # Verify the results
#     mediainfo test.wav
#     bwfmetaedit --out-core test.wav
#
# VALIDATION:
#     - Checks if file is a valid RIFF/WAV file
#     - Verifies bwfmetaedit is available
#     - Provides clear error messages for invalid files
#     - Confirms successful metadata writing
#
# TROUBLESHOOTING:
#     # Check if bwfmetaedit is installed
#     which bwfmetaedit
#     
#     # Install if missing (macOS)
#     brew install bwfmetaedit
#     
#     # Check file format
#     file test.wav  # Should show "RIFF (little-endian) data, WAVE audio"
#     
#     # Verify RIFF metadata was written
#     mediainfo test.wav  # Should show all metadata fields
#     bwfmetaedit --out-core test.wav  # Should show technical details
#
# NOTES:
#     - This script is idempotent - safe to run multiple times
#     - Original file is modified in place
#     - Always backup important files before running
#     - RIFF metadata is embedded in the WAV file header
#     - Field lengths are tested with 1000 characters
#     - Some fields may have format-specific limitations
#

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <wav_file>"
    exit 1
fi

# Resolve the file path and check if file exists
WAV_FILE=$(readlink -f "$1")
if [ ! -f "$WAV_FILE" ]; then
    echo "Error: File not found: $1"
    exit 1
fi

# Check if bwfmetaedit is available
if ! command -v bwfmetaedit &> /dev/null; then
    echo "Error: bwfmetaedit is required but not installed."
    exit 1
fi

# Check if it's a valid WAV file
if ! head -c 4 "$WAV_FILE" | grep -q "RIFF"; then
    echo "Error: Not a valid RIFF/WAV file"
    exit 1
fi

# Generate a string of 'a' characters for maximum length testing
STRING_BIG_LENGTH=$(printf 'a%.0s' {1..1000}) # 1000 to test truncation

echo "Setting metadata for: $WAV_FILE"

# Use bwfmetaedit to set all available RIFF INFO metadata fields
# Note: Removed trailing backslashes which could cause issues
bwfmetaedit \
    --INAM="$STRING_BIG_LENGTH" \
    --IART="$STRING_BIG_LENGTH" \
    --IPRD="$STRING_BIG_LENGTH" \
    --IGNR="$STRING_BIG_LENGTH" \
    --ICRD="9999" \
    --ICMT="$STRING_BIG_LENGTH" \
    --ISFT="$STRING_BIG_LENGTH" \
    --ICOP="$STRING_BIG_LENGTH" \
    --IENG="$STRING_BIG_LENGTH" \
    --ITCH="$STRING_BIG_LENGTH" \
    --ISRC="USXXX9999999" \
    --ISBJ="$STRING_BIG_LENGTH" \
    --IKEY="$STRING_BIG_LENGTH" \
    --IMED="$STRING_BIG_LENGTH" \
    --ICMS="$STRING_BIG_LENGTH" \
    --ITRK="99" \
    --IARL="$STRING_BIG_LENGTH" \
    --ILOC="$STRING_BIG_LENGTH" \
    "$WAV_FILE"

RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "All RIFF INFO tags written successfully with maximum length values"
    echo "Metadata setting completed successfully!"
else
    echo "Error: Failed to write RIFF INFO tags (exit code: $RESULT)"
    exit 1
fi