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