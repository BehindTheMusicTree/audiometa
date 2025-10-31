import pytest
from pathlib import Path
from unittest.mock import patch

from audiometa import AudioFile
from audiometa.manager.rating_supporting.Id3v2Manager import Id3v2Manager
from audiometa.manager.rating_supporting.VorbisManager import VorbisManager
from audiometa.manager.rating_supporting.RiffManager import RiffManager


@pytest.mark.unit
class TestGeneralHeaderMethods:

    @patch('audiometa.manager.rating_supporting.Id3v2Manager.ID3')
    def test_header_info_error_handling(self, mock_id3_class, mock_audio_file_mp3, mock_id3_empty):
        mock_id3_class.return_value = mock_id3_empty
        
        manager = Id3v2Manager(mock_audio_file_mp3)
        header_info = manager.get_header_info()
        
        assert isinstance(header_info, dict)
        assert 'present' in header_info

    @patch('audiometa.manager.rating_supporting.Id3v2Manager.ID3')
    def test_raw_metadata_info_error_handling(self, mock_id3_class, mock_audio_file_mp3, mock_id3_empty):
        mock_id3_class.return_value = mock_id3_empty
        
        manager = Id3v2Manager(mock_audio_file_mp3)
        raw_info = manager.get_raw_metadata_info()
        
        assert isinstance(raw_info, dict)
        assert 'raw_data' in raw_info

    @patch('audiometa.manager.rating_supporting.Id3v2Manager.ID3')
    def test_header_info_consistency(self, mock_id3_class, mock_audio_file_mp3, mock_id3_empty):
        mock_id3_class.return_value = mock_id3_empty
        
        manager = Id3v2Manager(mock_audio_file_mp3)
        header_info1 = manager.get_header_info()
        header_info2 = manager.get_header_info()
        
        assert header_info1 == header_info2

    @patch('audiometa.manager.rating_supporting.Id3v2Manager.ID3')
    def test_raw_metadata_info_consistency(self, mock_id3_class, mock_audio_file_mp3, mock_id3_empty):
        mock_id3_class.return_value = mock_id3_empty
        
        manager = Id3v2Manager(mock_audio_file_mp3)
        raw_info1 = manager.get_raw_metadata_info()
        raw_info2 = manager.get_raw_metadata_info()
        
        assert raw_info1 == raw_info2

    def test_header_info_with_different_file_types(self, sample_mp3_file: Path, sample_flac_file: Path, sample_wav_file: Path):
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