from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile


@pytest.mark.unit
class TestAudioFileChannels:
    def test_get_channels_mp3(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        channels = audio_file.get_channels()
        assert isinstance(channels, int)
        assert channels > 0

    def test_get_channels_flac(self, sample_flac_file: Path):
        audio_file = _AudioFile(sample_flac_file)
        channels = audio_file.get_channels()
        assert isinstance(channels, int)
        assert channels > 0

    def test_get_channels_wav(self, sample_wav_file: Path):
        audio_file = _AudioFile(sample_wav_file)
        channels = audio_file.get_channels()
        assert isinstance(channels, int)
        assert channels > 0

    def test_get_channels_returns_int(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        channels = audio_file.get_channels()
        assert isinstance(channels, int)
