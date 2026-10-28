from pathlib import Path

import pytest

from audiometa import get_duration_in_sec
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

    @pytest.mark.parametrize(
        "relative_path",
        [
            "sample.mp3",
            "shared/duration=277s.mp3",
            "shared/recording=Y do i - Carmina Burana Remix - 7m52.mp3",
            "shared/duration=182.mp3",
            "size_small=0.01mo.mp3",
            "sample.flac",
        ],
    )
    def test_get_duration_in_sec_matches_external_tool(self, assets_dir: Path, relative_path: str):
        file_path = assets_dir / relative_path
        external_tool_duration = TechnicalInfoInspector.get_duration(file_path)
        assert external_tool_duration is not None, "External tool (ffprobe) could not get duration"

        duration = get_duration_in_sec(file_path)
        assert duration == pytest.approx(external_tool_duration, abs=1e-3)

    def test_get_duration_in_sec_supports_all_formats(
        self, sample_mp3_file: Path, sample_flac_file: Path, sample_wav_file: Path
    ):
        mp3_duration = get_duration_in_sec(sample_mp3_file)
        flac_duration = get_duration_in_sec(sample_flac_file)
        wav_duration = get_duration_in_sec(sample_wav_file)

        assert isinstance(mp3_duration, float)
        assert isinstance(flac_duration, float)
        assert isinstance(wav_duration, float)
        assert all(d > 0 for d in [mp3_duration, flac_duration, wav_duration])
