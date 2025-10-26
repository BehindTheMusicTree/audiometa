"""Unit tests for ID3v2 metadata manager header information methods."""

from pathlib import Path

from audiometa import AudioFile
from audiometa.manager.rating_supporting.Id3v2Manager import Id3v2Manager


class TestId3v2HeaderMethods:
    """Test cases for ID3v2 metadata manager header information methods."""

    def test_id3v2_manager_header_info(self, sample_mp3_file: Path):
        """Test ID3v2Manager header info method."""
        audio_file = AudioFile(sample_mp3_file)
        manager = Id3v2Manager(audio_file)
        
        header_info = manager.get_header_info()
        
        # Should have ID3v2 specific structure
        assert 'present' in header_info
        assert 'version' in header_info
        assert 'header_size_bytes' in header_info
        assert 'flags' in header_info
        assert 'extended_header' in header_info
        
        # Should be valid structure
        assert isinstance(header_info['present'], bool)
        assert header_info['version'] is None or isinstance(header_info['version'], str)
        assert isinstance(header_info['header_size_bytes'], int)
        assert isinstance(header_info['flags'], dict)
        assert isinstance(header_info['extended_header'], dict)

    def test_id3v2_manager_raw_metadata_info(self, sample_mp3_file: Path):
        """Test ID3v2Manager raw metadata info method."""
        audio_file = AudioFile(sample_mp3_file)
        manager = Id3v2Manager(audio_file)
        
        raw_info = manager.get_raw_metadata_info()
        
        # Should have ID3v2 specific structure
        assert 'raw_data' in raw_info
        assert 'parsed_fields' in raw_info
        assert 'frames' in raw_info
        assert 'comments' in raw_info
        assert 'chunk_structure' in raw_info
        
        # Should be valid structure
        assert raw_info['raw_data'] is None or isinstance(raw_info['raw_data'], bytes)
        assert isinstance(raw_info['parsed_fields'], dict)
        assert isinstance(raw_info['frames'], dict)
        assert isinstance(raw_info['comments'], dict)
        assert isinstance(raw_info['chunk_structure'], dict)