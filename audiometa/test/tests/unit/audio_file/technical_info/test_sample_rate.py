from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile


@pytest.mark.unit
class TestAudioFileSampleRate:
    def test_get_sample_rate_mp3(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        sample_rate = audio_file.get_sample_rate()
        assert isinstance(sample_rate, int)
        assert sample_rate > 0

    def test_get_sample_rate_wav(self, sample_wav_file: Path):
        audio_file = _AudioFile(sample_wav_file)
        sample_rate = audio_file.get_sample_rate()
        assert isinstance(sample_rate, int)
        assert sample_rate > 0

    def test_get_sample_rate_flac(self, sample_flac_file: Path):
        audio_file = _AudioFile(sample_flac_file)
        sample_rate = audio_file.get_sample_rate()
        assert isinstance(sample_rate, int)
        assert sample_rate > 0

    def test_get_sample_rate_returns_int(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        sample_rate = audio_file.get_sample_rate()
        assert isinstance(sample_rate, int)
