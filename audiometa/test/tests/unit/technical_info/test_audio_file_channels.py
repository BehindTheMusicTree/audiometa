"""Unit tests for AudioFile get_channels method."""

import pytest
from pathlib import Path

from audiometa import AudioFile


@pytest.mark.unit
class TestAudioFileChannels:

    def test_get_channels_mp3(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        channels = audio_file.get_channels()
        
        assert isinstance(channels, int)
        assert channels > 0
        # Common channel counts: 1 (mono), 2 (stereo)
        assert channels in [1, 2, 4, 6, 8]

    def test_get_channels_wav(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        channels = audio_file.get_channels()
        
        assert isinstance(channels, int)
        assert channels > 0

    def test_get_channels_flac(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        channels = audio_file.get_channels()
        
        assert isinstance(channels, int)
        assert channels > 0