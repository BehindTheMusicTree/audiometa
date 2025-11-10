from pathlib import Path

import pytest

from audiometa import get_bitrate
from audiometa.test.helpers.technical_info_inspector import TechnicalInfoInspector


@pytest.mark.integration
class TestGetBitrate:
    def test_get_bitrate_works_with_path_string(self, sample_mp3_file: Path):
        bitrate = get_bitrate(str(sample_mp3_file))
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_works_with_pathlib_path(self, sample_mp3_file: Path):
        bitrate = get_bitrate(sample_mp3_file)
        assert isinstance(bitrate, int)
        assert bitrate > 0

    def test_get_bitrate_matches_external_tool(self, sample_mp3_file: Path):
        external_tool_bitrate = TechnicalInfoInspector.get_bitrate(sample_mp3_file)
        assert external_tool_bitrate == 128

        bitrate = get_bitrate(sample_mp3_file)
        assert bitrate == 127

    def test_get_bitrate_supports_all_formats(
        self, sample_mp3_file: Path, sample_flac_file: Path, sample_wav_file: Path
    ):
        mp3_bitrate = get_bitrate(sample_mp3_file)
        flac_bitrate = get_bitrate(sample_flac_file)
        wav_bitrate = get_bitrate(sample_wav_file)

        assert isinstance(mp3_bitrate, int)
        assert isinstance(flac_bitrate, int)
        assert isinstance(wav_bitrate, int)
        assert all(b > 0 for b in [mp3_bitrate, flac_bitrate, wav_bitrate])
