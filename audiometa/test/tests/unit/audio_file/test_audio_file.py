

import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.unit
class TestAudioFile:

    def test_audio_file_with_string_path(self, sample_mp3_file: Path):
        audio_file = AudioFile(str(sample_mp3_file))
        assert audio_file.file_path == str(sample_mp3_file)
        assert audio_file.file_extension == ".mp3"

    def test_audio_file_with_path_object(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        assert audio_file.file_path == str(sample_mp3_file)
        assert audio_file.file_extension == ".mp3"

    def test_audio_file_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            AudioFile("nonexistent_file.mp3")

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

    def test_file_operations(self, temp_audio_file: Path):
        audio_file = AudioFile(temp_audio_file)
        
        # Test write
        test_data = b"test audio data"
        bytes_written = audio_file.write(test_data)
        assert bytes_written == len(test_data)
        
        # Test read
        read_data = audio_file.read()
        assert read_data == test_data

    def test_file_name_methods(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        
        # Test system filename
        system_name = audio_file.get_file_name_system()
        assert system_name == sample_mp3_file.name
        
        # Test original filename (should be same as system for string paths)
        original_name = audio_file.get_file_name_original()
        assert original_name == sample_mp3_file.name

    def test_context_manager(self, sample_mp3_file: Path):
        with AudioFile(sample_mp3_file) as audio_file:
            assert audio_file.file_path == str(sample_mp3_file)
            # Context manager should work without issues

    def test_get_duration_in_sec_mp3(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_duration_in_sec_flac(self, sample_flac_file: Path):
        audio_file = AudioFile(sample_flac_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0

    def test_get_duration_in_sec_wav(self, sample_wav_file: Path):
        audio_file = AudioFile(sample_wav_file)
        duration = audio_file.get_duration_in_sec()
        assert isinstance(duration, float)
        assert duration > 0

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
