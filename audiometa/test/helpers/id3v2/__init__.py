"""ID3v2 metadata format helpers."""

# Core operations (following RIFF pattern)
# External tool wrappers
from ..common.external_tool_runner import ExternalMetadataToolError

# Advanced tools
from .id3v2_frame_manual_creator import ManualID3v2FrameCreator
from .id3v2_header_verifier import ID3v2HeaderVerifier
from .id3v2_metadata_deleter import ID3v2MetadataDeleter
from .id3v2_metadata_getter import ID3v2MetadataGetter
from .id3v2_metadata_setter import ID3v2MetadataSetter

# Specialized managers (moved to ID3v2MetadataSetter)


__all__ = [
    # Core operations
    "ID3v2HeaderVerifier",
    "ID3v2MetadataDeleter",
    "ID3v2MetadataSetter",
    "ID3v2MetadataGetter",
    # Specialized managers (moved to ID3v2MetadataSetter)
    # Advanced tools
    "ManualID3v2FrameCreator",
    # External tool wrappers
    "ExternalMetadataToolError",
]
