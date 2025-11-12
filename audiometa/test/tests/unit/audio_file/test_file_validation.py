from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile
from audiometa.exceptions import FileCorruptedError, FileTypeNotSupportedError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.unit
class TestAudioFileFileTypeValidation:
    def test_extension_mp3_then_ok(self, sample_mp3_file: Path):
        audio_file = _AudioFile(sample_mp3_file)
        assert audio_file.file_extension == ".mp3"

    def test_extension_flac_then_ok(self, sample_flac_file: Path):
        audio_file = _AudioFile(sample_flac_file)
        assert audio_file.file_extension == ".flac"

    def test_extension_wav_then_ok(self, sample_wav_file: Path):
        audio_file = _AudioFile(sample_wav_file)
        assert audio_file.file_extension == ".wav"

    def test_extension_m4a_then_not_ok(self, sample_m4a_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            _AudioFile(sample_m4a_file)

    def test_bad_content_then_not_ok(self):
        # Create a file with valid extension but bad content
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            temp_audio_file_path.write_bytes(b"not a real audio file")
            mp3_file_path = temp_audio_file_path.with_suffix(".mp3")
            mp3_file_path.write_bytes(b"not a real audio file")

            with pytest.raises(FileCorruptedError):
                _AudioFile(str(mp3_file_path))

    def test_nonexistent_file_raises_error(self):
        with pytest.raises(FileNotFoundError):
            _AudioFile("nonexistent.mp3")
