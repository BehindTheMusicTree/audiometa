"""Unit tests for metadata manager header information methods."""

import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.manager.MetadataManager import MetadataManager
from audiometa.manager.rating_supporting.Id3v2Manager import Id3v2Manager
from audiometa.manager.id3v1.Id3v1Manager import Id3v1Manager
from audiometa.manager.rating_supporting.VorbisManager import VorbisManager
from audiometa.manager.rating_supporting.RiffManager import RiffManager


class TestMetadataManagerHeaderMethods:
    """Test cases for metadata manager header information methods."""

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

    def test_id3v1_manager_header_info(self, sample_mp3_file: Path):
        """Test ID3v1Manager header info method."""
        audio_file = AudioFile(sample_mp3_file)
        manager = Id3v1Manager(audio_file)
        
        header_info = manager.get_header_info()
        
        # Should have ID3v1 specific structure
        assert 'present' in header_info
        assert 'position' in header_info
        assert 'size_bytes' in header_info
        assert 'version' in header_info
        assert 'has_track_number' in header_info
        
        # Should be valid structure
        assert isinstance(header_info['present'], bool)
        assert header_info['position'] is None or isinstance(header_info['position'], str)
        assert isinstance(header_info['size_bytes'], int)
        assert header_info['version'] is None or isinstance(header_info['version'], str)
        assert isinstance(header_info['has_track_number'], bool)

    def test_id3v1_manager_raw_metadata_info(self, sample_mp3_file: Path):
        """Test ID3v1Manager raw metadata info method."""
        audio_file = AudioFile(sample_mp3_file)
        manager = Id3v1Manager(audio_file)
        
        raw_info = manager.get_raw_metadata_info()
        
        # Should have ID3v1 specific structure
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

    def test_vorbis_manager_header_info(self, sample_flac_file: Path):
        """Test VorbisManager header info method."""
        audio_file = AudioFile(sample_flac_file)
        manager = VorbisManager(audio_file)
        
        header_info = manager.get_header_info()
        
        # Should have Vorbis specific structure
        assert 'present' in header_info
        assert 'vendor_string' in header_info
        assert 'comment_count' in header_info
        assert 'block_size' in header_info
        
        # Should be valid structure
        assert isinstance(header_info['present'], bool)
        assert header_info['vendor_string'] is None or isinstance(header_info['vendor_string'], str)
        assert isinstance(header_info['comment_count'], int)
        assert isinstance(header_info['block_size'], int)

    def test_vorbis_manager_raw_metadata_info(self, sample_flac_file: Path):
        """Test VorbisManager raw metadata info method."""
        audio_file = AudioFile(sample_flac_file)
        manager = VorbisManager(audio_file)
        
        raw_info = manager.get_raw_metadata_info()
        
        # Should have Vorbis specific structure
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

    def test_riff_manager_header_info(self, sample_wav_file: Path):
        """Test RiffManager header info method."""
        audio_file = AudioFile(sample_wav_file)
        manager = RiffManager(audio_file)
        
        header_info = manager.get_header_info()
        
        # Should have RIFF specific structure
        assert 'present' in header_info
        assert 'chunk_info' in header_info
        
        # Should be valid structure
        assert isinstance(header_info['present'], bool)
        assert isinstance(header_info['chunk_info'], dict)
        
        # Chunk info should have expected keys
        chunk_info = header_info['chunk_info']
        if header_info['present']:
            assert 'riff_chunk_size' in chunk_info
            assert 'info_chunk_size' in chunk_info
            assert 'audio_format' in chunk_info
            assert 'subchunk_size' in chunk_info

    def test_riff_manager_raw_metadata_info(self, sample_wav_file: Path):
        """Test RiffManager raw metadata info method."""
        audio_file = AudioFile(sample_wav_file)
        manager = RiffManager(audio_file)
        
        raw_info = manager.get_raw_metadata_info()
        
        # Should have RIFF specific structure
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

    def test_header_info_error_handling(self, sample_mp3_file: Path):
        """Test header info methods handle errors gracefully."""
        audio_file = AudioFile(sample_mp3_file)
        manager = Id3v2Manager(audio_file)
        
        # Should not raise exceptions even if underlying operations fail
        header_info = manager.get_header_info()
        assert isinstance(header_info, dict)
        assert 'present' in header_info

    def test_raw_metadata_info_error_handling(self, sample_mp3_file: Path):
        """Test raw metadata info methods handle errors gracefully."""
        audio_file = AudioFile(sample_mp3_file)
        manager = Id3v2Manager(audio_file)
        
        # Should not raise exceptions even if underlying operations fail
        raw_info = manager.get_raw_metadata_info()
        assert isinstance(raw_info, dict)
        assert 'raw_data' in raw_info

    def test_header_info_consistency(self, sample_mp3_file: Path):
        """Test that header info methods return consistent results."""
        audio_file = AudioFile(sample_mp3_file)
        manager = Id3v2Manager(audio_file)
        
        # Call multiple times
        header_info1 = manager.get_header_info()
        header_info2 = manager.get_header_info()
        
        # Should be identical
        assert header_info1 == header_info2

    def test_raw_metadata_info_consistency(self, sample_mp3_file: Path):
        """Test that raw metadata info methods return consistent results."""
        audio_file = AudioFile(sample_mp3_file)
        manager = Id3v2Manager(audio_file)
        
        # Call multiple times
        raw_info1 = manager.get_raw_metadata_info()
        raw_info2 = manager.get_raw_metadata_info()
        
        # Should be identical
        assert raw_info1 == raw_info2

    def test_header_info_with_different_file_types(self, sample_mp3_file: Path, sample_flac_file: Path, sample_wav_file: Path):
        """Test header info methods with different file types."""
        # Test MP3
        mp3_audio_file = AudioFile(sample_mp3_file)
        mp3_manager = Id3v2Manager(mp3_audio_file)
        mp3_header = mp3_manager.get_header_info()
        assert isinstance(mp3_header, dict)
        
        # Test FLAC
        flac_audio_file = AudioFile(sample_flac_file)
        flac_manager = VorbisManager(flac_audio_file)
        flac_header = flac_manager.get_header_info()
        assert isinstance(flac_header, dict)
        
        # Test WAV
        wav_audio_file = AudioFile(sample_wav_file)
        wav_manager = RiffManager(wav_audio_file)
        wav_header = wav_manager.get_header_info()
        assert isinstance(wav_header, dict)

    def test_raw_metadata_info_with_different_file_types(self, sample_mp3_file: Path, sample_flac_file: Path, sample_wav_file: Path):
        """Test raw metadata info methods with different file types."""
        # Test MP3
        mp3_audio_file = AudioFile(sample_mp3_file)
        mp3_manager = Id3v2Manager(mp3_audio_file)
        mp3_raw = mp3_manager.get_raw_metadata_info()
        assert isinstance(mp3_raw, dict)
        
        # Test FLAC
        flac_audio_file = AudioFile(sample_flac_file)
        flac_manager = VorbisManager(flac_audio_file)
        flac_raw = flac_manager.get_raw_metadata_info()
        assert isinstance(flac_raw, dict)
        
        # Test WAV
        wav_audio_file = AudioFile(sample_wav_file)
        wav_manager = RiffManager(wav_audio_file)
        wav_raw = wav_manager.get_raw_metadata_info()
        assert isinstance(wav_raw, dict)
