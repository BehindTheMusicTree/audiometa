"""Unit tests for _AudioFile get_audio_format_name method."""

from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile


@pytest.mark.unit
class TestAudioFileFormatName:
    def test_get_format_name_mp3(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        audio_format_name = audio_file.get_audio_format_name()

        assert audio_format_name == "MP3"

    def test_get_format_name_wav(self, sample_wav_file: Path):
        audio_file = _AudioFile(sample_wav_file)
        audio_format_name = audio_file.get_audio_format_name()

        assert audio_format_name == "WAV"

    def test_get_format_name_flac(self, sample_flac_file: Path):
        audio_file = _AudioFile(sample_flac_file)
        audio_format_name = audio_file.get_audio_format_name()

        assert audio_format_name == "FLAC"
