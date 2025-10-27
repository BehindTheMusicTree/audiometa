

import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.manager.rating_supporting.RiffManager import RiffManager
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.unit
class TestRiffManager:

    def test_riff_manager_wav(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        manager = RiffManager(audio_file)
        
        metadata = manager.get_unified_metadata()
        assert isinstance(metadata, dict)

    def test_riff_manager_unsupported_format(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        
        with pytest.raises(FileTypeNotSupportedError):
            RiffManager(audio_file)

    def test_riff_manager_update_metadata(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = RiffManager(audio_file)
            
            test_metadata = {
                UnifiedMetadataKey.TITLE: "RIFF Test Title",
                UnifiedMetadataKey.ARTISTS: ["RIFF Test Artist"],
                UnifiedMetadataKey.ALBUM: "RIFF Test Album"
            }
            
            manager.update_metadata(test_metadata)
            
            # Verify metadata was updated
            updated_metadata = manager.get_unified_metadata()
            assert updated_metadata.get(UnifiedMetadataKey.TITLE) == "RIFF Test Title"
            assert updated_metadata.get(UnifiedMetadataKey.ARTISTS) == ["RIFF Test Artist"]
            assert updated_metadata.get(UnifiedMetadataKey.ALBUM) == "RIFF Test Album"

    def test_riff_manager_rating_supported(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = RiffManager(audio_file, normalized_rating_max_value=100)
            
            test_metadata = {
                UnifiedMetadataKey.TITLE: "RIFF Test Title",
                UnifiedMetadataKey.RATING: 85  # RIFF supports rating through IRTD chunk
            }
            
            # This should work without raising an exception
            manager.update_metadata(test_metadata)
            
            # Verify metadata was updated
            updated_metadata = manager.get_unified_metadata()
            assert updated_metadata.get(UnifiedMetadataKey.TITLE) == "RIFF Test Title"
            assert updated_metadata.get(UnifiedMetadataKey.RATING) is not None
