

import pytest
from pathlib import Path

from audiometa import get_bitrate
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.unit
class TestBitrateFunctions:

    def test_get_bitrate_mp3(self, sample_mp3_file: Path):
        bitrate = get_bitrate(sample_mp3_file)
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_flac(self, sample_flac_file: Path):
        bitrate = get_bitrate(sample_flac_file)
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_wav(self, sample_wav_file: Path):
        bitrate = get_bitrate(sample_wav_file)
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_with_audio_file_object(self, sample_mp3_file: Path):
        from audiometa import AudioFile
        audio_file = AudioFile(sample_mp3_file)
        bitrate = get_bitrate(audio_file)
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        # Create a file with unsupported extension
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            get_bitrate(str(temp_audio_file))
