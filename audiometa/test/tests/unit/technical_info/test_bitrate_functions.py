

import pytest
from pathlib import Path

from audiometa import get_bitrate
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.technical_info_inspector import TechnicalInfoInspector


@pytest.mark.unit
class TestBitrateFunctions:

    def test_get_bitrate_mp3(self, sample_mp3_file: Path):
        external_tool_bitrate = TechnicalInfoInspector(sample_mp3_file).get_bitrate()
        assert external_tool_bitrate == 132
        
        bitrate = get_bitrate(sample_mp3_file)
        assert bitrate == 132

    def test_get_bitrate_flac(self, sample_flac_file: Path):
        external_tool_bitrate = TechnicalInfoInspector(sample_flac_file).get_bitrate()
        assert external_tool_bitrate == 1

        bitrate = get_bitrate(sample_flac_file)
        assert bitrate == 1

    def test_get_bitrate_wav(self, sample_wav_file: Path):
        external_tool_bitrate = TechnicalInfoInspector(sample_wav_file).get_bitrate()
        assert external_tool_bitrate == 128

        bitrate = get_bitrate(sample_wav_file)          
        assert bitrate == 128

    def test_get_bitrate_with_audio_file_object(self, sample_mp3_file: Path):
        from audiometa import AudioFile
        audio_file = AudioFile(sample_mp3_file)
        external_tool_bitrate = TechnicalInfoInspector(sample_mp3_file).get_bitrate()
        assert external_tool_bitrate == 132
        
        bitrate = get_bitrate(audio_file)
        assert bitrate == 132

    def test_get_bitrate_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        # Create a file with unsupported extension
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            get_bitrate(str(temp_audio_file))
