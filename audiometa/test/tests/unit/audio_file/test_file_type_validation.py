import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.unit
class TestAudioFileFileTypeValidation:

    def test_audio_file_unsupported_type(self, temp_audio_file: Path):
        # Create a file with unsupported extension
        temp_audio_file.write_bytes(b"fake audio content")
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            AudioFile(str(temp_audio_file))
    
    def test_valid_file_extension_mp3_then_ok(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        assert audio_file.file_extension == ".mp3"
    
    def test_valid_file_extension_flac_then_ok(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        assert audio_file.file_extension == ".flac"
    
    def test_valid_file_extension_wav_then_ok(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        assert audio_file.file_extension == ".wav"