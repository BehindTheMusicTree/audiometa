from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile


@pytest.mark.unit
class TestAudioFilePathHandling:
    def test_audio_file_with_string_path(self, sample_mp3_file: Path):
        sample_mp3_file_str = str(sample_mp3_file)
        audio_file = _AudioFile(sample_mp3_file_str)
        assert audio_file.file_path == sample_mp3_file_str
        assert audio_file.file_extension == ".mp3"

    def test_audio_file_with_path_object(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        assert audio_file.file_path == str(sample_mp3_file)
        assert audio_file.file_extension == ".mp3"

    def test_audio_file_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            _AudioFile("nonexistent_file.mp3")
