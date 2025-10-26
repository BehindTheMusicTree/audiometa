"""Unit tests for AudioFile get_sample_rate method."""

import pytest
from pathlib import Path

from audiometa import AudioFile


@pytest.mark.unit
class TestAudioFileSampleRate:

    def test_get_sample_rate_mp3(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        sample_rate = audio_file.get_sample_rate()
        
        assert isinstance(sample_rate, int)
        assert sample_rate > 0
        # Common sample rates: 44100, 48000, 22050, etc.
        assert sample_rate in [8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000, 88200, 96000]

    def test_get_sample_rate_wav(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        sample_rate = audio_file.get_sample_rate()
        
        assert isinstance(sample_rate, int)
        assert sample_rate > 0

    def test_get_sample_rate_flac(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        sample_rate = audio_file.get_sample_rate()
        
        assert isinstance(sample_rate, int)
        assert sample_rate > 0