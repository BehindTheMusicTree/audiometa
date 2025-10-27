import pytest
from pathlib import Path
from unittest.mock import patch

from audiometa import AudioFile


@pytest.mark.unit
class TestAudioFileOperations:

    def test_file_operations(self, temp_audio_file: Path):
        audio_file = AudioFile(temp_audio_file)
        
        # Test write
        test_data = b"test audio data"
        bytes_written = audio_file.write(test_data)
        assert bytes_written == len(test_data)
        
        # Test read
        read_data = audio_file.read()
        assert read_data == test_data