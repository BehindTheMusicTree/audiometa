"""Unit tests for AudioFile get_format_name method."""

import pytest
from pathlib import Path

from audiometa import AudioFile


@pytest.mark.unit
class TestAudioFileFormatName:

    def test_get_format_name_mp3(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        format_name = audio_file.get_format_name()
        
        assert format_name == 'MP3'

    def test_get_format_name_wav(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        format_name = audio_file.get_format_name()
        
        assert format_name == 'WAV'

    def test_get_format_name_flac(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        format_name = audio_file.get_format_name()
        
        assert format_name == 'FLAC'