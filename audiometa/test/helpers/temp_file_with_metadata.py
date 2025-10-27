"""Consolidated temporary file with metadata utilities for testing.

This module provides a unified TempFileWithMetadata class that combines
file management, external tool operations, and metadata verification
in a single, clean API.
"""

import subprocess
import tempfile
from pathlib import Path

from .id3v2 import ID3v2MetadataSetter
from .id3v1 import ID3v1MetadataSetter
from .vorbis import VorbisMetadataSetter
from .riff import RIFFMetadataSetter
from .common import AudioFileCreator
from .common.external_tool_runner import run_script


class TempFileWithMetadata:
    """Context manager for test files with comprehensive metadata operations.
    
    This class provides a unified interface for:
    - Creating temporary test files with metadata
    - Performing external tool operations
    - Verifying metadata and headers
    - Automatic cleanup
    
    Example:
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            # Set additional metadata using external tools
            test_file.set_id3v1_genre("17")
            test_file.set_id3v2_genre("Rock")
            
            # Verify headers
            assert test_file.has_id3v2_header()
            
            # Use test_file.path for testing
            metadata = get_unified_metadata(test_file.path)
    """
    
    def __init__(self, metadata: dict, format_type: str):
        """Initialize the context manager.
        
        Args:
            metadata: Dictionary of metadata to set on the test file
            format_type: Audio format ('mp3', 'id3v1', 'id3v2.3', 'id3v2.4', 'flac', 'wav')
        """
        self.metadata = metadata
        self.format_type = format_type
        self.test_file = None
    
    @property
    def path(self) -> Path:
        """Get the path to the test file.
        
        Returns:
            Path to the test file
        """
        if not self.test_file:
            raise RuntimeError("Test file not created yet. Use within context manager.")
        return self.test_file
    
    def __enter__(self):
        """Create the test file and return the manager instance.
        
        Returns:
            The TempFileWithMetadata instance for method access
        """
        self.test_file = self._create_test_file_with_metadata(self.metadata, self.format_type)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up the test file when exiting the context.
        
        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        if self.test_file and self.test_file.exists():
            self.test_file.unlink()
    
    def _create_test_file_with_metadata(self, metadata: dict, format_type: str) -> Path:
        """Create a test file with specific metadata values.
        
        This function uses external tools to set specific metadata values
        without using the app's update functions, improving test isolation.
        
        Args:
            metadata: Dictionary of metadata to set
            format_type: Audio format ('mp3', 'id3v1', 'flac', 'wav')
            
        Returns:
            Path to the created file with metadata
        """
        # Create temporary file with correct extension
        # For id3v1, id3v2.3, id3v2.4, use .mp3 extension since they're still MP3 files
        if format_type.lower() in ['id3v1', 'id3v2.3', 'id3v2.4']:
            actual_extension = 'mp3'
        else:
            actual_extension = format_type.lower()
        with tempfile.NamedTemporaryFile(suffix=f'.{actual_extension}', delete=False) as tmp_file:
            target_file = Path(tmp_file.name)
        
        self._create_minimal_audio_file(target_file, format_type)
        
        if format_type.lower() == 'mp3':
            ID3v2MetadataSetter.set_metadata(target_file, metadata)
        elif format_type.lower() == 'id3v1':
            self._set_mp3_metadata_id3v1(target_file, metadata)
        elif format_type.lower() in ['id3v2.3', 'id3v2.4']:
            # Use version-specific ID3v2 metadata setting
            version = format_type.lower().replace('id3v2.', '2.')
            ID3v2MetadataSetter.set_metadata(target_file, metadata, version)
        elif format_type.lower() == 'flac':
            self._set_flac_metadata_with_metaflac(target_file, metadata)
        elif format_type.lower() == 'wav':
            self._set_wav_metadata_with_bwfmetaedit(target_file, metadata)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
        
        return target_file
    
    def _set_mp3_metadata_id3v1(self, file_path: Path, metadata: dict) -> None:
        ID3v1MetadataSetter.set_metadata(file_path, metadata)
    
    def _set_flac_metadata_with_metaflac(self, file_path: Path, metadata: dict) -> None:
        VorbisMetadataSetter.set_flac_metadata(file_path, metadata)
    
    def _set_wav_metadata_with_bwfmetaedit(self, file_path: Path, metadata: dict) -> None:
        RIFFMetadataSetter.set_wav_metadata(file_path, metadata)
    
    def _create_minimal_audio_file(self, file_path: Path, format_type: str) -> None:
        test_files_dir = Path(__file__).parent.parent.parent / "test" / "data" / "audio_files"
        AudioFileCreator.create_minimal_audio_file(file_path, format_type, test_files_dir)
    
    def _get_scripts_dir(self) -> Path:
        return Path(__file__).parent.parent.parent / "test" / "data" / "scripts"
    
    def _run_script(self, script_name: str) -> subprocess.CompletedProcess:
        """Run an external script with proper error handling."""
        scripts_dir = self._get_scripts_dir()
        # Use the unified run_script function for script execution
        return run_script(script_name, self.test_file, scripts_dir)
    
    def _create_multiple_id3v2_frames(self, frame_id: str, texts: list[str]) -> None:
        """Create multiple separate ID3v2 frames using manual binary construction.
        
        This uses the ManualID3v2FrameCreator to bypass standard tools that 
        consolidate multiple frames of the same type, allowing creation of 
        truly separate frames for testing purposes.
        
        Args:
            frame_id: The ID3v2 frame identifier (e.g., 'TPE1', 'TPE2', 'TCON', 'TCOM')
            texts: List of text values, one per frame
        """
        ID3v2MetadataSetter._create_multiple_id3v2_frames(self.test_file, frame_id, texts)
    


