import pytest
from pathlib import Path
from unittest.mock import patch

from audiometa import AudioFile
from audiometa.manager.rating_supporting.Id3v2Manager import Id3v2Manager
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter


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

    def test_id3v2_manager_read_title(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_title(test_file.path, "Test Title ID3v2")
            
            audio_file = AudioFile(test_file.path)
            manager = Id3v2Manager(audio_file)
            title = manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
            
            assert title == "Test Title ID3v2"

    def test_id3v2_manager_read_artists(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_metadata(test_file.path, {UnifiedMetadataKey.ARTISTS: ["Artist 1", "Artist 2"]})
            
            audio_file = AudioFile(test_file.path)
            manager = Id3v2Manager(audio_file)
            artists = manager.get_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
            
            assert artists == ["Artist 1", "Artist 2"]

    def test_id3v2_manager_write_title(self):
        from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
        
        with TempFileWithMetadata({}, "mp3") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = Id3v2Manager(audio_file)
            manager.update_metadata({UnifiedMetadataKey.TITLE: "Written Title"})
            
            title = ID3v2MetadataGetter.get_title(test_file.path)
            assert title == "Written Title"

    def test_id3v2_manager_write_artists(self):
        from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
        
        with TempFileWithMetadata({}, "mp3") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = Id3v2Manager(audio_file)
            manager.update_metadata({UnifiedMetadataKey.ARTISTS: ["Written Artist 1", "Written Artist 2"]})
            
            artists_2_3 = ID3v2MetadataGetter.get_artists(test_file.path, version='2.3')
            artists_2_4 = ID3v2MetadataGetter.get_artists(test_file.path, version='2.4')
            
            artists = artists_2_3 or artists_2_4
            assert artists is not None
            assert "Written Artist 1" in artists
            assert "Written Artist 2" in artists
