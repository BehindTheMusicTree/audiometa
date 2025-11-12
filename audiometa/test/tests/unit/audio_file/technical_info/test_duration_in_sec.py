from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile


@pytest.mark.unit
class TestAudioFileDurationInSec:
    def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0
        assert duration < 1000  # Reasonable bounds check

    def test_get_duration_in_sec_flac(self, sample_flac_file: Path):
        audio_file = _AudioFile(sample_flac_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_duration_in_sec_wav(self, sample_wav_file: Path):
        audio_file = _AudioFile(sample_wav_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_duration_in_sec_long_file(self, duration_182s_mp3: Path):
        audio_file = _AudioFile(duration_182s_mp3)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 100

    def test_get_duration_in_sec_returns_float(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
