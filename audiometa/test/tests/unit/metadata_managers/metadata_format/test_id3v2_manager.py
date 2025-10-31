import pytest
from unittest.mock import patch, MagicMock

from audiometa import AudioFile
from audiometa.manager.rating_supporting.Id3v2Manager import Id3v2Manager
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.unit
class TestId3v2Manager:

    @patch('audiometa.manager.rating_supporting.Id3v2Manager.ID3')
    def test_id3v2_manager_mp3(self, mock_id3_class, mock_audio_file_mp3, mock_id3_empty):
        mock_id3_class.return_value = mock_id3_empty
        
        manager = Id3v2Manager(mock_audio_file_mp3)
        metadata = manager.get_unified_metadata()
        
        assert isinstance(metadata, dict)
        mock_id3_class.assert_called_once_with(mock_audio_file_mp3.file_path, load_v1=False, translate=False)

    @patch('audiometa.manager.rating_supporting.Id3v2Manager.ID3')
    def test_id3v2_manager_wav(self, mock_id3_class, mock_audio_file_wav, mock_id3_empty):
        mock_id3_class.return_value = mock_id3_empty
        
        manager = Id3v2Manager(mock_audio_file_wav)
        metadata = manager.get_unified_metadata()
        
        assert isinstance(metadata, dict)
        mock_id3_class.assert_called_once_with(mock_audio_file_wav.file_path, load_v1=False, translate=False)

    @patch('audiometa.manager.rating_supporting.Id3v2Manager.ID3')
    def test_id3v2_manager_with_rating_normalization(self, mock_id3_class, mock_audio_file_mp3, mock_id3_empty):
        mock_id3_class.return_value = mock_id3_empty
        
        manager = Id3v2Manager(mock_audio_file_mp3, normalized_rating_max_value=100)
        metadata = manager.get_unified_metadata()
        
        assert isinstance(metadata, dict)
        assert manager.normalized_rating_max_value == 100

    @patch('audiometa.manager.rating_supporting.Id3v2Manager.ID3')
    def test_id3v2_manager_extracts_metadata(self, mock_id3_class, mock_audio_file_mp3, mock_id3_with_metadata):
        mock_id3_class.return_value = mock_id3_with_metadata
        
        manager = Id3v2Manager(mock_audio_file_mp3)
        metadata = manager.get_unified_metadata()
        
        assert isinstance(metadata, dict)

    @patch('audiometa.manager.rating_supporting.Id3v2Manager.ID3')
    def test_id3v2_manager_update_metadata(self, mock_id3_class, mock_audio_file_mp3, mock_id3_updatable):
        mock_id3_class.return_value = mock_id3_updatable
        
        manager = Id3v2Manager(mock_audio_file_mp3, normalized_rating_max_value=100)
        
        # Mock the file operations
        with patch.object(manager, '_preserve_id3v1_metadata', return_value=None), \
             patch.object(manager, '_save_with_id3v1_preservation'):
            
            test_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v2 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v2 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v2 Test Album",
                UnifiedMetadataKey.RATING: 80,
                UnifiedMetadataKey.BPM: 120
            }
            
            manager.update_metadata(test_metadata)
            
            # Verify metadata was updated
            updated_metadata = manager.get_unified_metadata()
            assert updated_metadata.get(UnifiedMetadataKey.TITLE) == "ID3v2 Test Title"
            assert updated_metadata.get(UnifiedMetadataKey.ARTISTS) == ["ID3v2 Test Artist"]
            assert updated_metadata.get(UnifiedMetadataKey.ALBUM) == "ID3v2 Test Album"
            assert updated_metadata.get(UnifiedMetadataKey.RATING) == 80
            assert updated_metadata.get(UnifiedMetadataKey.BPM) == 120
