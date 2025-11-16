"""Test configuration for audiometa-python tests."""

import importlib.util
import sys
from pathlib import Path

import pytest

# Import the shared verification script
project_root = Path(__file__).parent.parent.parent.parent
verify_script_path = project_root / "scripts" / "verify-system-dependency-versions.py"

# Load the module dynamically
spec = importlib.util.spec_from_file_location("verify_system_dependency_versions", verify_script_path)
verify_module = importlib.util.module_from_spec(spec)
sys.modules["verify_system_dependency_versions"] = verify_module
spec.loader.exec_module(verify_module)  # type: ignore[union-attr]

verify_dependency_versions = verify_module.verify_dependency_versions


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    """Verify system dependency versions match pinned versions before running tests."""
    exit_code = verify_dependency_versions()
    if exit_code != 0:
        pytest.exit("Dependency version verification failed. See errors above.", returncode=exit_code)


def pytest_collection_modifyitems(items):
    """Reorder test items to ensure proper execution order: unit → integration → e2e."""
    # Define the desired test execution order based on directory structure
    test_order = {"unit": 1, "integration": 2, "e2e": 3}

    def get_test_priority(item):
        """Get the priority order for a test item based on its path."""
        test_path = str(item.fspath)

        # Check for unit tests
        if "/unit/" in test_path:
            return test_order["unit"]
        # Check for integration tests
        if "/integration/" in test_path:
            return test_order["integration"]
        # Check for e2e tests
        if "/e2e/" in test_path:
            return test_order["e2e"]
        # Default priority for other tests (comprehensive, etc.)
        return 0  # Run first (before unit tests)

    # Sort items by priority
    items.sort(key=get_test_priority)


@pytest.fixture
def assets_dir() -> Path:
    return Path(__file__).parent.parent.parent / "test" / "assets"


@pytest.fixture
def sample_mp3_file(assets_dir: Path) -> Path:
    return assets_dir / "sample.mp3"


@pytest.fixture
def sample_flac_file(assets_dir: Path) -> Path:
    return assets_dir / "sample.flac"


@pytest.fixture
def sample_wav_file(assets_dir: Path) -> Path:
    return assets_dir / "sample.wav"


@pytest.fixture
def sample_m4a_file(assets_dir: Path) -> Path:
    return assets_dir / "sample.m4a"


@pytest.fixture
def metadata_id3v1_big_mp3(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v1_big.mp3"


@pytest.fixture
def metadata_id3v1_small_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v1_small.flac"


@pytest.fixture
def metadata_id3v1_big_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v1_big.flac"


@pytest.fixture
def metadata_id3v1_small_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v1_small.wav"


@pytest.fixture
def metadata_id3v1_big_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v1_big.wav"


@pytest.fixture
def metadata_id3v2_small_mp3(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_small.mp3"


@pytest.fixture
def metadata_id3v2_big_mp3(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_big.mp3"


@pytest.fixture
def metadata_id3v2_small_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_small.flac"


@pytest.fixture
def metadata_id3v2_big_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_big.flac"


@pytest.fixture
def metadata_id3v2_small_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_small.wav"


@pytest.fixture
def metadata_id3v2_big_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_big.wav"


@pytest.fixture
def metadata_id3v2_and_riff_small_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_and_riff_small.wav"


@pytest.fixture
def metadata_riff_small_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_riff_small.wav"


@pytest.fixture
def metadata_riff_big_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_riff_big.wav"


@pytest.fixture
def metadata_vorbis_small_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_vorbis_small.flac"


@pytest.fixture
def metadata_vorbis_big_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_vorbis_big.flac"


@pytest.fixture
def artists_one_two_three_comma_id3v2(assets_dir: Path) -> Path:
    return assets_dir / "artists=One Two Three_comma_id3v2.mp3"


@pytest.fixture
def artists_one_two_three_semicolon_id3v2(assets_dir: Path) -> Path:
    return assets_dir / "artists=One Two Three_semicolon_id3v2.mp3"


@pytest.fixture
def artists_one_two_three_multi_tags_vorbis(assets_dir: Path) -> Path:
    return assets_dir / "artists=One Two Three_muti tags_vorbis.flac"


@pytest.fixture
def album_koko_id3v2_mp3(assets_dir: Path) -> Path:
    return assets_dir / "album=koko_id3v2.mp3"


@pytest.fixture
def album_koko_id3v2_wav(assets_dir: Path) -> Path:
    return assets_dir / "album=koko_id3v2.wav"


@pytest.fixture
def album_koko_vorbis_flac(assets_dir: Path) -> Path:
    return assets_dir / "album=koko_vorbis.flac"


@pytest.fixture
def genre_code_id3v1_abstract_mp3(assets_dir: Path) -> Path:
    return assets_dir / "genre_code_id3v1=Abstract.mp3"


@pytest.fixture
def genre_code_id3v1_unknown_mp3(assets_dir: Path) -> Path:
    return assets_dir / "genre_code_id3v1=Unknown.mp3"


@pytest.fixture
def duration_1s_mp3(assets_dir: Path) -> Path:
    return assets_dir / "duration=1s.wav"


@pytest.fixture
def duration_182s_mp3(assets_dir: Path) -> Path:
    return assets_dir / "duration=182.mp3"


@pytest.fixture
def duration_335s_flac(assets_dir: Path) -> Path:
    return assets_dir / "duration=335s.flac"


@pytest.fixture
def duration_472s_wav(assets_dir: Path) -> Path:
    return assets_dir / "duration=472s.wav"


@pytest.fixture
def bitrate_320_mp3(assets_dir: Path) -> Path:
    return assets_dir / "bitrate in kbps_big=320.mp3"


@pytest.fixture
def bitrate_946_flac(assets_dir: Path) -> Path:
    return assets_dir / "bitrate in kbps_big=946.flac"


@pytest.fixture
def bitrate_1411_wav(assets_dir: Path) -> Path:
    return assets_dir / "bitrate in kbps_big=1411.wav"


@pytest.fixture
def size_small_mp3(assets_dir: Path) -> Path:
    return assets_dir / "size_small=0.01mo.mp3"


@pytest.fixture
def size_big_mp3(assets_dir: Path) -> Path:
    return assets_dir / "size_big=9.98mo.mp3"


@pytest.fixture
def size_small_flac(assets_dir: Path) -> Path:
    return assets_dir / "size_small=0.05mo.flac"


@pytest.fixture
def size_big_flac(assets_dir: Path) -> Path:
    return assets_dir / "size_big=26.6mo.flac"


@pytest.fixture
def size_small_wav(assets_dir: Path) -> Path:
    return assets_dir / "size_small=0.08mo.wav"


@pytest.fixture
def size_big_wav(assets_dir: Path) -> Path:
    return assets_dir / "size_big=79.55mo.wav"
