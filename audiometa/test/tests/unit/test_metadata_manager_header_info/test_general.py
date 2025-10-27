"""Unit tests for general metadata manager header information methods."""

from pathlib import Path

from audiometa import AudioFile
from audiometa.manager.rating_supporting.Id3v2Manager import Id3v2Manager
from audiometa.manager.id3v1.Id3v1Manager import Id3v1Manager
from audiometa.manager.rating_supporting.VorbisManager import VorbisManager
from audiometa.manager.rating_supporting.RiffManager import RiffManager
import pytest


@pytest.mark.unit
class TestGeneralHeaderMethods:
    """Test cases for general metadata manager header information methods."""

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