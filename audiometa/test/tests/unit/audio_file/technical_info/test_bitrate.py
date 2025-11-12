from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile


@pytest.mark.unit
class TestAudioFileBitrate:
    def test_get_bitrate_mp3(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        bitrate = audio_file.get_bitrate()
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_flac(self, sample_flac_file: Path):
        audio_file = _AudioFile(sample_flac_file)
        bitrate = audio_file.get_bitrate()
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_wav(self, sample_wav_file: Path):
        audio_file = _AudioFile(sample_wav_file)
        bitrate = audio_file.get_bitrate()
        assert isinstance(bitrate, int)
        assert bitrate > 0
