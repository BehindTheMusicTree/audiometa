import pytest
from pathlib import Path

from audiometa import AudioFile


@pytest.mark.unit
class TestMp3Metadata:

    def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_bitrate_mp3(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        bitrate = audio_file.get_bitrate()
        assert isinstance(bitrate, int)
        assert bitrate > 0