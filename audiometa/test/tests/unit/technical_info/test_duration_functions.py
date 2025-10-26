

import pytest
from pathlib import Path

from audiometa import get_duration_in_sec
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.unit
class TestDurationFunctions:

    def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
        duration = get_duration_in_sec(sample_mp3_file)
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_duration_in_sec_flac(self, sample_flac_file: Path):
        duration = get_duration_in_sec(sample_flac_file)
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_duration_in_sec_wav(self, sample_wav_file: Path):
        duration = get_duration_in_sec(sample_wav_file)
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_duration_in_sec_with_audio_file_object(self, sample_mp3_file: Path):
        from audiometa import AudioFile
        audio_file = AudioFile(sample_mp3_file)
        duration = get_duration_in_sec(audio_file)
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_duration_in_sec_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        # Create a file with unsupported extension
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            get_duration_in_sec(str(temp_audio_file))
