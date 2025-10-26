"""Unit tests for AudioFile get_file_size method."""

import pytest
from pathlib import Path
import os

from audiometa import AudioFile


@pytest.mark.unit
class TestAudioFileFileSize:

    def test_get_file_size(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        file_size = audio_file.get_file_size()
        
        assert isinstance(file_size, int)
        assert file_size > 0
        
        # Should match actual file size
        actual_size = os.path.getsize(sample_mp3_file)
        assert file_size == actual_size