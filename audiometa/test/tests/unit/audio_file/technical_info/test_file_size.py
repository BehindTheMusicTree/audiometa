from pathlib import Path

import pytest

from audiometa import get_file_size
from audiometa.test.helpers.technical_info_inspector import TechnicalInfoInspector


@pytest.mark.unit
class TestFileSizeFunctions:
    def test_file_size_mp3(self, sample_mp3_file: Path):
        external_tool_size = TechnicalInfoInspector.get_file_size(sample_mp3_file)
        assert external_tool_size == 17307

        file_size = get_file_size(sample_mp3_file)
        assert file_size == 17307

    def test_file_size_mp3_big(self, size_big_mp3: Path):
        external_tool_size = TechnicalInfoInspector.get_file_size(size_big_mp3)
        assert external_tool_size == 10468959

        file_size = get_file_size(size_big_mp3)
        assert file_size == 10468959

    def test_file_size_flac(self, sample_flac_file: Path):
        external_tool_size = TechnicalInfoInspector.get_file_size(sample_flac_file)
        assert external_tool_size == 18439

        file_size = get_file_size(sample_flac_file)
        assert file_size == 18439

    def test_file_size_flac_big(self, size_big_flac: Path):
        external_tool_size = TechnicalInfoInspector.get_file_size(size_big_flac)
        assert external_tool_size == 27888561

        file_size = get_file_size(size_big_flac)
        assert file_size == 27888561

    def test_file_size_wav(self, sample_wav_file: Path):
        external_tool_size = TechnicalInfoInspector.get_file_size(sample_wav_file)
        assert external_tool_size == 16822

        file_size = get_file_size(sample_wav_file)
        assert file_size == 16822

    def test_file_size_wav_big(self, size_big_wav: Path):
        external_tool_size = TechnicalInfoInspector.get_file_size(size_big_wav)
        assert external_tool_size == 83414326

        file_size = get_file_size(size_big_wav)
        assert file_size == 83414326
