

import pytest
from unittest.mock import patch, MagicMock

from audiometa import AudioFile
from audiometa.manager.rating_supporting.RiffManager import RiffManager
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.unit
class TestRiffManager:

    @patch('audiometa.manager.rating_supporting.RiffManager.WAVE')
    def test_riff_manager_wav(self, mock_wave_class, mock_audio_file_wav, mock_wave_empty):
        mock_wave_class.return_value = mock_wave_empty
        
        # Mock file operations
        with patch.object(mock_audio_file_wav, 'seek'), \
             patch.object(mock_audio_file_wav, 'read', return_value=b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00'):
            
            manager = RiffManager(mock_audio_file_wav)
            metadata = manager.get_unified_metadata()
            
            assert isinstance(metadata, dict)
            mock_wave_class.assert_called_once()

    @patch('audiometa.manager.rating_supporting.RiffManager.WAVE')
    def test_riff_manager_unsupported_format(self, mock_wave_class, mock_audio_file_mp3):
        with pytest.raises(FileTypeNotSupportedError):
            RiffManager(mock_audio_file_mp3)

    @patch('audiometa.manager.rating_supporting.RiffManager.WAVE')
    def test_riff_manager_update_metadata(self, mock_wave_class, mock_audio_file_wav, mock_wave_empty):
        mock_wave_class.return_value = mock_wave_empty
        
        # Mock file operations
        with patch.object(mock_audio_file_wav, 'seek'), \
             patch.object(mock_audio_file_wav, 'read', return_value=b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00'), \
             patch.object(mock_audio_file_wav, 'write'):
            
            manager = RiffManager(mock_audio_file_wav)
            
            test_metadata = {
                UnifiedMetadataKey.TITLE: "RIFF Test Title",
                UnifiedMetadataKey.ARTISTS: ["RIFF Test Artist"],
                UnifiedMetadataKey.ALBUM: "RIFF Test Album"
            }
            
            manager.update_metadata(test_metadata)

    def test_riff_manager_read_title(self):
        from audiometa.test.helpers.riff import RIFFMetadataSetter
        
        with TempFileWithMetadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_title(test_file.path, "Test Title RIFF")
            
            audio_file = AudioFile(test_file.path)
            manager = RiffManager(audio_file)
            title = manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
            
            assert title == "Test Title RIFF"

    def test_riff_manager_read_artists(self):
        from audiometa.test.helpers.riff import RIFFMetadataSetter
        
        with TempFileWithMetadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_metadata(test_file.path, {UnifiedMetadataKey.ARTISTS: ["Artist 1", "Artist 2"]})
            
            audio_file = AudioFile(test_file.path)
            manager = RiffManager(audio_file)
            artists = manager.get_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
            
            assert artists == ["Artist 1", "Artist 2"]

    def test_riff_manager_write_title(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = RiffManager(audio_file)
            manager.update_metadata({UnifiedMetadataKey.TITLE: "Written Title"})
            
            new_manager = RiffManager(AudioFile(test_file.path))
            title = new_manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
            assert title == "Written Title"

    def test_riff_manager_write_artists(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = RiffManager(audio_file)
            manager.update_metadata({UnifiedMetadataKey.ARTISTS: ["Written Artist 1", "Written Artist 2"]})
            
            new_manager = RiffManager(AudioFile(test_file.path))
            artists = new_manager.get_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
            assert artists == ["Written Artist 1", "Written Artist 2"]