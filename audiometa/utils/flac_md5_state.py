"""FLAC MD5 checksum validation state enumeration.

This module defines the possible states of MD5 checksum validation for FLAC files.
"""

from enum import Enum


class FlacMd5State(str, Enum):
    """Enumeration of FLAC MD5 checksum validation states.

    FLAC files can have MD5 checksums in different states:
    - VALID: The checksum is set and matches the audio data
    - UNSET: The checksum is all zeros (not set)
    - UNCHECKABLE_DUE_TO_ID3V1: The checksum is set but cannot be validated due to ID3v1 tags
    - INVALID: The checksum is set but doesn't match the audio data (corrupted)
    """

    VALID = "valid"
    UNSET = "unset"
    UNCHECKABLE_DUE_TO_ID3V1 = "uncheckable_due_to_id3v1"
    INVALID = "invalid"
