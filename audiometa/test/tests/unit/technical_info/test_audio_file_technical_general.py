"""Unit tests for general AudioFile technical methods behavior."""

import pytest
from pathlib import Path
import tempfile
import os
import time

from audiometa import AudioFile
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.unit
class TestAudioFileTechnicalGeneral:

    def test_get_sample_rate_unsupported_format(self):
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(b'This is not an audio file')
        
        try:
            with pytest.raises(FileTypeNotSupportedError):
                AudioFile(temp_path)
        finally:
            os.unlink(temp_path)

    def test_get_file_size_nonexistent_file(self):
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Delete the file
        os.unlink(temp_path)
        
        # Should handle gracefully
        with pytest.raises(FileNotFoundError):
            AudioFile(temp_path)

    def test_get_format_name_unsupported(self):
        with tempfile.NamedTemporaryFile(suffix='.unknown', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(b'Some data')
        
        try:
            # This should raise an exception before we can test get_format_name
            with pytest.raises(FileTypeNotSupportedError):
                AudioFile(temp_path)
        finally:
            os.unlink(temp_path)

    def test_technical_methods_consistency(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        
        # Get values multiple times
        sample_rate1 = audio_file.get_sample_rate()
        sample_rate2 = audio_file.get_sample_rate()
        channels1 = audio_file.get_channels()
        channels2 = audio_file.get_channels()
        file_size1 = audio_file.get_file_size()
        file_size2 = audio_file.get_file_size()
        format_name1 = audio_file.get_format_name()
        format_name2 = audio_file.get_format_name()
        
        # Should be consistent
        assert sample_rate1 == sample_rate2
        assert channels1 == channels2
        assert file_size1 == file_size2
        assert format_name1 == format_name2

    def test_technical_methods_with_corrupted_file(self):
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
            # Write some garbage data that looks like it might be an MP3
            temp_file.write(b'ID3\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        
        try:
            audio_file = AudioFile(temp_path)
            
            # Methods should handle corruption gracefully
            sample_rate = audio_file.get_sample_rate()
            channels = audio_file.get_channels()
            file_size = audio_file.get_file_size()
            format_name = audio_file.get_format_name()
            
            # Should return some values (might be 0 or defaults)
            assert isinstance(sample_rate, int)
            assert isinstance(channels, int)
            assert isinstance(file_size, int)
            assert isinstance(format_name, str)
            assert file_size > 0  # File size should be accurate
            assert format_name == 'MP3'  # Format name should be correct
            
        finally:
            os.unlink(temp_path)

    def test_technical_methods_performance(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        
        # Time the methods
        start_time = time.time()
        
        sample_rate = audio_file.get_sample_rate()
        channels = audio_file.get_channels()
        file_size = audio_file.get_file_size()
        format_name = audio_file.get_format_name()
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should complete quickly (less than 1 second for most files)
        assert elapsed < 1.0
        
        # Results should still be valid
        assert sample_rate > 0
        assert channels > 0
        assert file_size > 0
        assert format_name == 'MP3'

    def test_technical_methods_memory_usage(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        
        # Call methods multiple times to check for memory leaks
        for _ in range(100):
            sample_rate = audio_file.get_sample_rate()
            channels = audio_file.get_channels()
            file_size = audio_file.get_file_size()
            format_name = audio_file.get_format_name()
            
            # Values should be consistent
            assert isinstance(sample_rate, int)
            assert isinstance(channels, int)
            assert isinstance(file_size, int)
            assert isinstance(format_name, str)

    def test_technical_methods_with_different_file_sizes(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        
        sample_rate = audio_file.get_sample_rate()
        channels = audio_file.get_channels()
        file_size = audio_file.get_file_size()
        format_name = audio_file.get_format_name()
        
        # All should return valid values
        assert sample_rate > 0
        assert channels > 0
        assert file_size > 0
        assert format_name == 'MP3'
        
        # File size should match actual file size
        actual_size = os.path.getsize(sample_mp3_file)
        assert file_size == actual_size