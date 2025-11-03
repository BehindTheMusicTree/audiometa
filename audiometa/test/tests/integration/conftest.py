import pytest

from pathlib import Path


# Test tracks with no metadata
@pytest.fixture
def metadata_none_mp3(assets_dir: Path) -> Path:
    return assets_dir / "metadata=none.mp3"


@pytest.fixture
def metadata_none_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=none.flac"


@pytest.fixture
def metadata_none_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=none.wav"