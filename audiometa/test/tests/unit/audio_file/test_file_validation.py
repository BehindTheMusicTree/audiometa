import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.exceptions import FileCorruptedError, FileTypeNotSupportedError


@pytest.mark.unit
class TestAudioFileFileTypeValidation:
    
    def test_extension_mp3_then_ok(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        assert audio_file.file_extension == ".mp3"
    
    def test_extension_flac_then_ok(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        assert audio_file.file_extension == ".flac"
    
    def test_extension_wav_then_ok(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        assert audio_file.file_extension == ".wav"

    def test_extension_m4a_then_not_ok(self, sample_m4a_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            AudioFile(sample_m4a_file)
            
    def test_bad_content_then_not_ok(self, temp_audio_file: Path):
        # Create a file with valid extension but bad content
        temp_audio_file.write_bytes(b"not a real audio file")
        temp_audio_file = temp_audio_file.with_suffix(".mp3")
        temp_audio_file.write_bytes(b"not a real audio file")
        
        with pytest.raises(FileCorruptedError):
            AudioFile(str(temp_audio_file))

    def test_nonexistent_file_raises_error(self):
        with pytest.raises(FileNotFoundError):
            AudioFile("nonexistent.mp3")