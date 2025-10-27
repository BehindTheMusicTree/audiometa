import pytest
from pathlib import Path

from audiometa import AudioFile


@pytest.mark.unit
class TestWavMetadata:

    def test_get_duration_in_sec_wav(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_bitrate_wav(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        bitrate = audio_file.get_bitrate()
        assert isinstance(bitrate, int)
        assert bitrate > 0