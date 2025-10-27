

import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.unit
class TestAudioFileChannels:

    def test_get_channels_mp3(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        channels = audio_file.get_channels()
        assert isinstance(channels, int)
        assert channels > 0

    def test_get_channels_flac(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        channels = audio_file.get_channels()
        assert isinstance(channels, int)
        assert channels > 0

    def test_get_channels_wav(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        channels = audio_file.get_channels()
        assert isinstance(channels, int)
        assert channels > 0

    def test_get_channels_returns_int(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        channels = audio_file.get_channels()
        assert isinstance(channels, int)

    def test_get_channels_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            AudioFile(temp_audio_file).get_channels()

    def test_get_channels_nonexistent_file_raises_error(self):
        with pytest.raises(FileNotFoundError):
            AudioFile("nonexistent.mp3").get_channels()