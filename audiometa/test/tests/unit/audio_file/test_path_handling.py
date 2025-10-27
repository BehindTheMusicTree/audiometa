import pytest
from pathlib import Path

from audiometa import AudioFile


@pytest.mark.unit
class TestAudioFilePathHandling:

    def test_audio_file_with_string_path(self, sample_mp3_file: Path):
        audio_file = AudioFile(str(sample_mp3_file))
        assert audio_file.file_path == str(sample_mp3_file)
        assert audio_file.file_extension == ".mp3"

    def test_audio_file_with_path_object(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        assert audio_file.file_path == str(sample_mp3_file)
        assert audio_file.file_extension == ".mp3"

    def test_audio_file_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            AudioFile("nonexistent_file.mp3")