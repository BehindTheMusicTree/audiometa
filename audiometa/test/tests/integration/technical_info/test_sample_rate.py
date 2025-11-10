from pathlib import Path

import pytest

from audiometa import get_sample_rate
from audiometa.test.helpers.technical_info_inspector import TechnicalInfoInspector


@pytest.mark.integration
class TestGetSampleRate:
    def test_get_sample_rate_works_with_path_string(self, sample_mp3_file: Path):
        sample_rate = get_sample_rate(str(sample_mp3_file))
        assert isinstance(sample_rate, int)
        assert sample_rate > 0

    def test_get_sample_rate_works_with_pathlib_path(self, sample_mp3_file: Path):
        sample_rate = get_sample_rate(sample_mp3_file)
        assert isinstance(sample_rate, int)
        assert sample_rate > 0

    def test_get_sample_rate_matches_external_tool(self, sample_mp3_file: Path):
        external_sample_rate = TechnicalInfoInspector.get_sample_rate(sample_mp3_file)
        assert external_sample_rate is not None
        assert isinstance(external_sample_rate, int)
        assert external_sample_rate == 44100

        sample_rate = get_sample_rate(sample_mp3_file)
        assert sample_rate == external_sample_rate

    def test_get_sample_rate_supports_all_formats(
        self, sample_mp3_file: Path, sample_flac_file: Path, sample_wav_file: Path
    ):
        mp3_sample_rate = get_sample_rate(sample_mp3_file)
        flac_sample_rate = get_sample_rate(sample_flac_file)
        wav_sample_rate = get_sample_rate(sample_wav_file)

        assert isinstance(mp3_sample_rate, int)
        assert isinstance(flac_sample_rate, int)
        assert isinstance(wav_sample_rate, int)
        assert all(r > 0 for r in [mp3_sample_rate, flac_sample_rate, wav_sample_rate])
