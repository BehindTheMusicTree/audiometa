"""Unit tests for AudioFile get_channels method."""

import pytest
from pathlib import Path

from audiometa import get_channels
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.technical_info_inspector import TechnicalInfoInspector


@pytest.mark.unit
class TestChannelsFunctions:

    def test_channels_mp3(self, sample_mp3_file: Path):
        external_tool_channels = TechnicalInfoInspector.get_channels(sample_mp3_file)
        assert external_tool_channels == 2
        
        channels = get_channels(sample_mp3_file)
        assert channels == 2

    def test_channels_flac_low_bitrate(self, sample_flac_file: Path):
        external_tool_channels = TechnicalInfoInspector.get_channels(sample_flac_file)
        assert external_tool_channels == 2

        channels = get_channels(sample_flac_file)
        assert channels == 2

    def test_channels_flac_high_bitrate(self, size_big_flac: Path):
        external_tool_channels = TechnicalInfoInspector.get_channels(size_big_flac)
        assert external_tool_channels == 2

        channels = get_channels(size_big_flac)
        assert channels == 2

    def test_channels_wav(self, sample_wav_file: Path):
        external_tool_channels = TechnicalInfoInspector.get_channels(sample_wav_file)
        assert external_tool_channels == 2

        channels = get_channels(sample_wav_file)          
        assert channels == 2

    def test_channels_with_audio_file_object(self, sample_mp3_file: Path):
        from audiometa import AudioFile
        audio_file = AudioFile(sample_mp3_file)
        external_tool_channels = TechnicalInfoInspector.get_channels(sample_mp3_file)
        assert external_tool_channels == 2
        
        channels = get_channels(audio_file)
        assert channels == 2

    def test_channels_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        # Create a file with unsupported extension
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            get_channels(str(temp_audio_file))