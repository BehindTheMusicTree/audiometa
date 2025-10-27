

import pytest
from pathlib import Path

from audiometa import get_sample_rate, AudioFile
from audiometa.test.helpers.technical_info_inspector import TechnicalInfoInspector


@pytest.mark.integration
class TestGetSampleRate:
    
    def test_get_sample_rate_mp3(self, sample_mp3_file: Path):
        external_sample_rate = TechnicalInfoInspector.get_sample_rate(sample_mp3_file)
        assert external_sample_rate is not None
        assert isinstance(external_sample_rate, int)
        assert external_sample_rate == 44100
        
        sample_rate = get_sample_rate(sample_mp3_file)
        assert sample_rate == external_sample_rate
    
    def test_get_sample_rate_wav(self, sample_wav_file: Path):
        external_sample_rate = TechnicalInfoInspector.get_sample_rate(sample_wav_file)
        assert external_sample_rate is not None
        assert isinstance(external_sample_rate, int)
        assert external_sample_rate == 44100
        
        sample_rate = get_sample_rate(sample_wav_file)
        assert sample_rate == external_sample_rate
    
    def test_get_sample_rate_flac(self, sample_flac_file: Path):
        external_sample_rate = TechnicalInfoInspector.get_sample_rate(sample_flac_file)
        assert external_sample_rate is not None
        assert isinstance(external_sample_rate, int)
        assert external_sample_rate == 44100
        
        sample_rate = get_sample_rate(sample_flac_file)
        assert sample_rate == external_sample_rate
    
    def test_get_sample_rate_with_string_path(self, sample_mp3_file: Path):
        sample_rate = get_sample_rate(str(sample_mp3_file))
        assert isinstance(sample_rate, int)
        assert sample_rate > 0
    
    def test_get_sample_rate_with_pathlib_path(self, sample_mp3_file: Path):
        sample_rate = get_sample_rate(sample_mp3_file)
        assert isinstance(sample_rate, int)
        assert sample_rate > 0

