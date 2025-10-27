import pytest
from pathlib import Path

from audiometa import AudioFile


@pytest.mark.unit
class TestAudioFileNames:

    def test_file_name_methods(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        
        # Test system filename
        system_name = audio_file.get_file_name_system()
        assert system_name == sample_mp3_file.name
        
        # Test original filename (should be same as system for string paths)
        original_name = audio_file.get_file_name_original()
        assert original_name == sample_mp3_file.name