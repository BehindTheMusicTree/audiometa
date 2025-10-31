

import pytest
from unittest.mock import patch, MagicMock

from audiometa import AudioFile
from audiometa.manager.rating_supporting.VorbisManager import VorbisManager
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.unit
class TestVorbisManager:

    def test_vorbis_manager_flac(self, mocker, mock_audio_file_flac, mock_vorbis_metadata_empty):
        # Mock the metadata extraction to avoid file I/O
        mocker.patch.object(VorbisManager, '_extract_mutagen_metadata', return_value=mock_vorbis_metadata_empty)
        
        manager = VorbisManager(mock_audio_file_flac)
        metadata = manager.get_unified_metadata()
        
        assert isinstance(metadata, dict)

    def test_vorbis_manager_update_metadata(self, mocker, mock_audio_file_flac, mock_vorbis_metadata_empty):
        # Mock the metadata extraction and external tool calls
        mocker.patch.object(VorbisManager, '_extract_mutagen_metadata', return_value=mock_vorbis_metadata_empty)
        mocker.patch.object(VorbisManager, '_write_metadata_with_metaflac')
        
        manager = VorbisManager(mock_audio_file_flac, normalized_rating_max_value=100)
        
        test_metadata = {
            UnifiedMetadataKey.TITLE: "Vorbis Test Title",
            UnifiedMetadataKey.ARTISTS: ["Vorbis Test Artist"],
            UnifiedMetadataKey.ALBUM: "Vorbis Test Album",
            UnifiedMetadataKey.RATING: 60,
            UnifiedMetadataKey.BPM: 140
        }
        
        manager.update_metadata(test_metadata)
