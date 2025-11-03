

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

    def test_vorbis_manager_read_title(self):
        from audiometa.test.helpers.vorbis import VorbisMetadataSetter
        
        with TempFileWithMetadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_title(test_file.path, "Test Title Vorbis")
            
            audio_file = AudioFile(test_file.path)
            manager = VorbisManager(audio_file)
            title = manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
            
            assert title == "Test Title Vorbis"

    def test_vorbis_manager_read_artists(self):
        from audiometa.test.helpers.vorbis import VorbisMetadataSetter
        
        with TempFileWithMetadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_metadata(test_file.path, {UnifiedMetadataKey.ARTISTS: ["Artist 1", "Artist 2"]})
            
            audio_file = AudioFile(test_file.path)
            manager = VorbisManager(audio_file)
            artists = manager.get_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
            
            assert artists == ["Artist 1", "Artist 2"]

    def test_vorbis_manager_write_title(self):
        from mutagen.flac import FLAC
        
        with TempFileWithMetadata({}, "flac") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = VorbisManager(audio_file)
            manager.update_metadata({UnifiedMetadataKey.TITLE: "Written Title"})
            
            audio = FLAC(str(test_file.path))
            assert 'TITLE' in audio
            assert audio['TITLE'][0] == "Written Title"

    def test_vorbis_manager_write_artists(self):
        from mutagen.flac import FLAC
        
        with TempFileWithMetadata({}, "flac") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = VorbisManager(audio_file)
            manager.update_metadata({UnifiedMetadataKey.ARTISTS: ["Written Artist 1", "Written Artist 2"]})
            
            audio = FLAC(str(test_file.path))
            artists = audio.get('ARTIST', [])
            assert "Written Artist 1" in artists
            assert "Written Artist 2" in artists
