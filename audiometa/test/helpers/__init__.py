"""Test helpers package for audiometa.

This package provides utilities for creating and managing test files with metadata.
Classes are organized by metadata format in subdirectories following clean architecture principles.

Main Classes:
- TempFileWithMetadata: Context manager for test files with comprehensive metadata operations
  Located in: temp_file_with_metadata.py

Organized by Format:

ID3v1 Format (id3v1/):
- Id3v1Tool: Wrapper for id3v1 operations using id3v2 tool
- ID3v1MetadataDeleter: Deleting ID3v1 metadata

ID3v2 Format (id3v2/):
- ID3v2MetadataVerifier: Verifying ID3v2 metadata
- ID3v2MetadataSetter: Setting ID3v2 metadata including multiple frame values

- ManualID3v2FrameCreator: Manual binary construction of ID3v2 frames for testing edge cases
- ID3HeaderVerifier: Verifying ID3v1/ID3v2 headers

Vorbis Format (vorbis/):
- VorbisMetadataSetter: Setting Vorbis metadata and managing multiple Vorbis comment values
- VorbisMetadataDeleter: Deleting Vorbis metadata
- VorbisHeaderVerifier: Verifying Vorbis comment headers and retrieving metadata information
- VorbisMetadataVerifier: Verifying Vorbis comments

RIFF Format (riff/):
- RIFFMetadataVerifier: Verifying RIFF metadata
- RIFFMetadataSetter: Setting RIFF metadata, managing separator-based metadata, and managing multiple RIFF chunk values
- RIFFMetadataDeleter: Deleting RIFF metadata
- RIFFHeaderVerifier: Verifying RIFF INFO chunk headers and retrieving metadata information

Common Utilities (common/):
- AudioFileCreator: Utilities for creating minimal audio files
- ComprehensiveMetadataVerifier: Cross-format comprehensive verification and header detection
- run_script: Unified function for running external scripts with proper error handling

Usage:
    from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
    from audiometa.test.helpers.id3v1 import Id3v1Tool, ID3v1MetadataDeleter
    from audiometa.test.helpers.id3v2 import (
        ID3v2MetadataVerifier, ID3v2MetadataSetter, ManualID3v2FrameCreator, ID3HeaderVerifier
    )
    from audiometa.test.helpers.vorbis import (
        VorbisMetadataSetter, VorbisMetadataDeleter, VorbisHeaderVerifier, VorbisMetadataVerifier
    )
    from audiometa.test.helpers.riff import RIFFMetadataVerifier, RIFFHeaderVerifier
    from audiometa.test.helpers.common import AudioFileCreator, ComprehensiveMetadataVerifier, run_script
"""
