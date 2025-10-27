

import pytest
from pathlib import Path

from audiometa import get_duration_in_sec, AudioFile
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.technical_info_inspector import TechnicalInfoInspector


@pytest.mark.integration
class TestGetDurationInSec:
    
    def test_get_duration_in_sec_works_with_path_string(self, sample_mp3_file: Path):
        duration = get_duration_in_sec(str(sample_mp3_file))
        assert isinstance(duration, float)
        assert duration > 0
    
    def test_get_duration_in_sec_works_with_pathlib_path(self, sample_mp3_file: Path):
        duration = get_duration_in_sec(sample_mp3_file)
        assert isinstance(duration, float)
        assert duration > 0
    
    def test_get_duration_in_sec_works_with_audio_file_object(self, sample_mp3_file: Path):
        audio_file = AudioFile(sample_mp3_file)
        duration = get_duration_in_sec(audio_file)
        assert isinstance(duration, float)
        assert duration > 0
    
    def test_get_duration_in_sec_matches_external_tool(self, sample_mp3_file: Path):
        external_tool_duration = TechnicalInfoInspector.get_duration(sample_mp3_file)
        assert external_tool_duration == 1.045
        
        duration = get_duration_in_sec(sample_mp3_file)
        assert duration == pytest.approx(1.0448979591836736, rel=1e-6)
    
    def test_get_duration_in_sec_supports_all_formats(self, sample_mp3_file: Path, sample_flac_file: Path, sample_wav_file: Path):
        mp3_duration = get_duration_in_sec(sample_mp3_file)
        flac_duration = get_duration_in_sec(sample_flac_file)
        wav_duration = get_duration_in_sec(sample_wav_file)
        
        assert isinstance(mp3_duration, float)
        assert isinstance(flac_duration, float)
        assert isinstance(wav_duration, float)
        assert all(d > 0 for d in [mp3_duration, flac_duration, wav_duration])
    
    def test_get_duration_in_sec_unsupported_file_type_raises_error(self, temp_audio_file: Path):
        temp_audio_file = temp_audio_file.with_suffix(".txt")
        temp_audio_file.write_bytes(b"fake audio content")
        
        with pytest.raises(FileTypeNotSupportedError):
            get_duration_in_sec(str(temp_audio_file))

