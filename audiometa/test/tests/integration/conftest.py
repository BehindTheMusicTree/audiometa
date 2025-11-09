from pathlib import Path

import pytest


# Test tracks with rating
@pytest.fixture
def rating_id3v2_base_100_0_star_wav(assets_dir: Path) -> Path:
    return assets_dir / "rating_id3v2_base 100=0 star.wav"


@pytest.fixture
def rating_id3v2_base_100_5_star_wav(assets_dir: Path) -> Path:
    return assets_dir / "rating_id3v2_base 100=5 star.wav"


@pytest.fixture
def rating_id3v2_base_255_5_star_mp3(assets_dir: Path) -> Path:
    return assets_dir / "rating_id3v2_base 255_kid3=5 star.mp3"


@pytest.fixture
def rating_riff_base_100_5_star_wav(assets_dir: Path) -> Path:
    return assets_dir / "rating_riff_base 100_kid3=5 star.wav"


@pytest.fixture
def rating_vorbis_base_100_5_star_flac(assets_dir: Path) -> Path:
    return assets_dir / "rating_vorbis=5 star.flac"
