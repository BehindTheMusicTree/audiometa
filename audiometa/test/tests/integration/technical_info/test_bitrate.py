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

    def test_get_bitrate_for_320_kbps_mp3(self, bitrate_320_mp3: Path):
        """Test bitrate for 320 kbps MP3 file."""
        bitrate = get_bitrate(bitrate_320_mp3)
        assert isinstance(bitrate, int)
        # Expected: 320 kbps (based on filename convention)
        assert bitrate == 320, f"Expected 320 kbps, got {bitrate} kbps"

    def test_get_bitrate_for_946_kbps_flac(self, bitrate_946_flac: Path):
        """Test bitrate for 946 kbps FLAC file."""
        bitrate = get_bitrate(bitrate_946_flac)
        assert isinstance(bitrate, int)
        # Expected: 946 kbps (based on filename convention)
        assert bitrate == 946, f"Expected 946 kbps, got {bitrate} kbps"

    def test_get_bitrate_for_1411_kbps_wav(self, bitrate_1411_wav: Path):
        """Test bitrate for 1411 kbps WAV file."""
        bitrate = get_bitrate(bitrate_1411_wav)
        assert isinstance(bitrate, int)
        # Expected: 1411 kbps (based on filename convention)
        assert bitrate == 1411, f"Expected 1411 kbps, got {bitrate} kbps"

    def test_get_bitrate_validates_across_all_test_assets(self, assets_dir: Path):
        """Test bitrate for all dedicated bitrate test assets."""
        bitrate_test_files = [
            ("bitrate in kbps_big=320.mp3", 320),
            ("bitrate in kbps_big=946.flac", 946),
            ("bitrate in kbps_big=1411.wav", 1411),
            ("bitrate in kbps_small=192.mp3", 192),
            ("bitrate in kbps_small=723.flac", 723),
            ("bitrate in kbps_small=1152.wav", 1152),
        ]

        for filename, expected_bitrate in bitrate_test_files:
            file_path = assets_dir / filename
            if file_path.exists():
                bitrate = get_bitrate(file_path)
                assert isinstance(bitrate, int), f"Bitrate for {filename} should be int"
                assert (
                    bitrate == expected_bitrate
                ), f"Expected {expected_bitrate} kbps for {filename}, got {bitrate} kbps"
