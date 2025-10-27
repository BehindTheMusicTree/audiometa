

import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.unit
class TestAudioFileBitrate:

    def test_get_bitrate_mp3(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        bitrate = audio_file.get_bitrate()
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_flac(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        bitrate = audio_file.get_bitrate()
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_wav(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        bitrate = audio_file.get_bitrate()
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_returns_int(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        bitrate = audio_file.get_bitrate()
        assert isinstance(bitrate, int)

    def test_get_bitrate_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            AudioFile(temp_audio_file).get_bitrate()

    def test_get_bitrate_nonexistent_file_raises_error(self):
        with pytest.raises(FileNotFoundError):
            AudioFile("nonexistent.mp3").get_bitrate()
