import pytest

from pathlib import Path


# Test tracks with no metadata
@pytest.fixture
def metadata_none_mp3(test_files_dir: Path) -> Path:
    return test_files_dir / "metadata=none.mp3"


@pytest.fixture
def metadata_none_flac(test_files_dir: Path) -> Path:
    return test_files_dir / "metadata=none.flac"


@pytest.fixture
def metadata_none_wav(test_files_dir: Path) -> Path:
    return test_files_dir / "metadata=none.wav"