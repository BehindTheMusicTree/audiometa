from pathlib import Path

import pytest

from audiometa import get_channels
from audiometa.test.helpers.technical_info_inspector import TechnicalInfoInspector


@pytest.mark.integration
class TestGetChannels:
    def test_get_channels_works_with_path_string(self, sample_mp3_file: Path):
        channels = get_channels(str(sample_mp3_file))
        assert isinstance(channels, int)
        assert channels > 0

    def test_get_channels_works_with_pathlib_path(self, sample_mp3_file: Path):
        channels = get_channels(sample_mp3_file)
        assert isinstance(channels, int)
        assert channels > 0

    def test_get_channels_matches_external_tool(self, sample_mp3_file: Path):
        external_tool_channels = TechnicalInfoInspector.get_channels(sample_mp3_file)
        assert external_tool_channels == 2

        channels = get_channels(sample_mp3_file)
        assert channels == 2

    def test_get_channels_supports_all_formats(
        self, sample_mp3_file: Path, sample_flac_file: Path, sample_wav_file: Path
    ):
        mp3_channels = get_channels(sample_mp3_file)
        flac_channels = get_channels(sample_flac_file)
        wav_channels = get_channels(sample_wav_file)

        assert isinstance(mp3_channels, int)
        assert isinstance(flac_channels, int)
        assert isinstance(wav_channels, int)
        assert all(c > 0 for c in [mp3_channels, flac_channels, wav_channels])
