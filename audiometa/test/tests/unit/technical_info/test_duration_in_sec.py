

import pytest
from pathlib import Path

from audiometa import get_duration_in_sec
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.technical_info_inspector import TechnicalInfoInspector


@pytest.mark.unit
class TestDurationInSecFunctions:

    def test_duration_in_sec_mp3(self, sample_mp3_file: Path):
        external_tool_duration = TechnicalInfoInspector.get_duration(sample_mp3_file)
        assert external_tool_duration == 1.045
        
        duration = get_duration_in_sec(sample_mp3_file)
        assert duration == pytest.approx(1.0448979591836736, rel=1e-6)

    def test_duration_in_sec_mp3_long(self, duration_182s_mp3: Path):
        external_tool_duration = TechnicalInfoInspector.get_duration(duration_182s_mp3)
        assert external_tool_duration == 181.734
        
        duration = get_duration_in_sec(duration_182s_mp3)
        assert duration == pytest.approx(181.69614512471657, rel=1e-6)

    def test_duration_in_sec_flac(self, sample_flac_file: Path):
        external_tool_duration = TechnicalInfoInspector.get_duration(sample_flac_file)
        assert external_tool_duration == 1.0

        duration = get_duration_in_sec(sample_flac_file)
        assert duration == 1.0

    def test_duration_in_sec_flac_long(self, duration_335s_flac: Path):
        external_tool_duration = TechnicalInfoInspector.get_duration(duration_335s_flac)
        assert external_tool_duration == 335.213

        duration = get_duration_in_sec(duration_335s_flac)
        assert duration == pytest.approx(335.2133333333333, rel=1e-6)

    def test_duration_in_sec_wav(self, sample_wav_file: Path):
        external_tool_duration = TechnicalInfoInspector.get_duration(sample_wav_file)
        assert external_tool_duration == 1.045

        duration = get_duration_in_sec(sample_wav_file)          
        assert duration == pytest.approx(1.025057, rel=1e-6)

    def test_duration_in_sec_wav_long(self, duration_472s_wav: Path):
        external_tool_duration = TechnicalInfoInspector.get_duration(duration_472s_wav)
        assert external_tool_duration == 472.560

        duration = get_duration_in_sec(duration_472s_wav)          
        assert duration == pytest.approx(472.56, rel=1e-6)

    def test_duration_in_sec_with_audio_file_object(self, sample_mp3_file: Path):
        from audiometa import AudioFile
        audio_file = AudioFile(sample_mp3_file)
        external_tool_duration = TechnicalInfoInspector.get_duration(sample_mp3_file)
        assert external_tool_duration == 1.045
        
        duration = get_duration_in_sec(audio_file)
        assert duration == pytest.approx(1.0448979591836736, rel=1e-6)

    def test_duration_in_sec_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        # Create a file with unsupported extension
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            get_duration_in_sec(str(temp_audio_file))
