

import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.manager.rating_supporting.VorbisManager import VorbisManager
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.unit
class TestVorbisManager:

    def test_vorbis_manager_flac(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        manager = VorbisManager(audio_file)
        
        metadata = manager.get_unified_metadata()
        assert isinstance(metadata, dict)


    def test_vorbis_manager_with_rating_normalization(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        manager = VorbisManager(audio_file, normalized_rating_max_value=100)
        
        metadata = manager.get_unified_metadata()
        assert isinstance(metadata, dict)

    def test_vorbis_manager_update_metadata(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = VorbisManager(audio_file, normalized_rating_max_value=100)
            
            test_metadata = {
                UnifiedMetadataKey.TITLE: "Vorbis Test Title",
                UnifiedMetadataKey.ARTISTS: ["Vorbis Test Artist"],
                UnifiedMetadataKey.ALBUM: "Vorbis Test Album",
                UnifiedMetadataKey.RATING: 60,
                UnifiedMetadataKey.BPM: 140
            }
            
            manager.update_metadata(test_metadata)
            
            # Verify metadata was updated
            updated_metadata = manager.get_unified_metadata()
            assert updated_metadata.get(UnifiedMetadataKey.TITLE) == "Vorbis Test Title"
            assert updated_metadata.get(UnifiedMetadataKey.ARTISTS) == ["Vorbis Test Artist"]
            assert updated_metadata.get(UnifiedMetadataKey.ALBUM) == "Vorbis Test Album"
            assert updated_metadata.get(UnifiedMetadataKey.RATING) == 60
            assert updated_metadata.get(UnifiedMetadataKey.BPM) == 140
