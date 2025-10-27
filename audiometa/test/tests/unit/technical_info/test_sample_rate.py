"""Unit tests for AudioFile get_sample_rate method."""

import pytest
from pathlib import Path

from audiometa import get_sample_rate
from audiometa.test.helpers.technical_info_inspector import TechnicalInfoInspector

@pytest.mark.unit
class TestAudioFileSampleRate:

    def test_sample_rate_mp3(self, sample_mp3_file: Path):
        # First assert against external tool (mediainfo)
        external_sample_rate = TechnicalInfoInspector.get_sample_rate(sample_mp3_file)
        assert external_sample_rate is not None, "mediainfo should return sample rate"
        assert isinstance(external_sample_rate, int)
        assert external_sample_rate == 44100
        
        # Then assert library function matches
        library_sample_rate = get_sample_rate(sample_mp3_file)
        assert library_sample_rate == external_sample_rate

    def test_sample_rate_wav(self, sample_wav_file: Path):
        # First assert against external tool (mediainfo)
        external_sample_rate = TechnicalInfoInspector.get_sample_rate(sample_wav_file)
        assert external_sample_rate is not None, "mediainfo should return sample rate"
        assert isinstance(external_sample_rate, int)
        assert external_sample_rate == 44100
        
        # Then assert library function matches
        library_sample_rate = get_sample_rate(sample_wav_file)
        assert library_sample_rate == external_sample_rate

    def test_sample_rate_flac(self, sample_flac_file: Path):
        # First assert against external tool (mediainfo)
        external_sample_rate = TechnicalInfoInspector.get_sample_rate(sample_flac_file)
        assert external_sample_rate is not None, "mediainfo should return sample rate"
        assert isinstance(external_sample_rate, int)
        assert external_sample_rate == 44100
        
        # Then assert library function matches
        library_sample_rate = get_sample_rate(sample_flac_file)
        assert library_sample_rate == external_sample_rate