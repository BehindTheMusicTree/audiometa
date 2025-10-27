

import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.unit
class TestAudioFileDurationInSec:
    
    def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0
        assert duration < 1000  # Reasonable bounds check
    
    def test_get_duration_in_sec_flac(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0
    
    def test_get_duration_in_sec_wav(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0
    
    def test_get_duration_in_sec_long_file(self, duration_182s_mp3: Path):
        audio_file = AudioFile(duration_182s_mp3)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 100
    
    def test_get_duration_in_sec_returns_float(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
    
    def test_get_duration_in_sec_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            AudioFile(temp_audio_file).get_duration_in_sec()
    
    def test_get_duration_in_sec_nonexistent_file_raises_error(self):
        with pytest.raises(FileNotFoundError):
            AudioFile("nonexistent.mp3").get_duration_in_sec()
