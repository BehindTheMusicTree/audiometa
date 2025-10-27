"""Test configuration for audiometa-python tests."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


def pytest_collection_modifyitems(items):
    """Reorder test items to ensure proper execution order: unit → integration → e2e."""
    # Define the desired test execution order based on directory structure
    TEST_ORDER = {
        "unit": 1,
        "integration": 2, 
        "e2e": 3
    }
    
    def get_test_priority(item):
        """Get the priority order for a test item based on its path."""
        test_path = str(item.fspath)
        
        # Check for unit tests
        if "/unit/" in test_path:
            return TEST_ORDER["unit"]
        # Check for integration tests  
        elif "/integration/" in test_path:
            return TEST_ORDER["integration"]
        # Check for e2e tests
        elif "/e2e/" in test_path:
            return TEST_ORDER["e2e"]
        # Default priority for other tests (comprehensive, etc.)
        else:
            return 0  # Run first (before unit tests)
    
    # Sort items by priority
    items.sort(key=get_test_priority)


@pytest.fixture
def test_files_dir() -> Path:
    """Return the path to the test audio files directory."""
    return Path(__file__).parent.parent.parent / "test" / "assets"


@pytest.fixture
def temp_audio_file() -> Generator[Path, None, None]:
    """Create a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        temp_path = Path(tmp_file.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_wav_file() -> Generator[Path, None, None]:
    """Create a temporary WAV file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        temp_path = Path(tmp_file.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_flac_file() -> Generator[Path, None, None]:
    """Create a temporary FLAC file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as tmp_file:
        temp_path = Path(tmp_file.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


# Basic sample files
@pytest.fixture
def sample_mp3_file(test_files_dir: Path) -> Path:
    """Return path to a sample MP3 file."""
    return test_files_dir / "sample.mp3"


@pytest.fixture
def sample_flac_file(test_files_dir: Path) -> Path:
    """Return path to a sample FLAC file."""
    return test_files_dir / "sample.flac"


@pytest.fixture
def sample_wav_file(test_files_dir: Path) -> Path:
    """Return path to a sample WAV file."""
    return test_files_dir / "sample.wav"


# Test tracks with no metadata
@pytest.fixture
def metadata_none_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with no metadata."""
    return test_files_dir / "metadata=none.mp3"


@pytest.fixture
def metadata_none_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with no metadata."""
    return test_files_dir / "metadata=none.flac"


@pytest.fixture
def metadata_none_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with no metadata."""
    return test_files_dir / "metadata=none.wav"


# Test tracks with ID3v1 metadata
@pytest.fixture
def metadata_id3v1_small_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with ID3v1 metadata (small)."""
    return test_files_dir / "metadata=long a_id3v1_small.mp3"


@pytest.fixture
def metadata_id3v1_big_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with ID3v1 metadata (big)."""
    return test_files_dir / "metadata=long a_id3v1_big.mp3"


@pytest.fixture
def metadata_id3v1_small_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with ID3v1 metadata (small)."""
    return test_files_dir / "metadata=long a_id3v1_small.flac"


@pytest.fixture
def metadata_id3v1_big_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with ID3v1 metadata (big)."""
    return test_files_dir / "metadata=long a_id3v1_big.flac"


@pytest.fixture
def metadata_id3v1_small_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with ID3v1 metadata (small)."""
    return test_files_dir / "metadata=long a_id3v1_small.wav"


@pytest.fixture
def metadata_id3v1_big_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with ID3v1 metadata (big)."""
    return test_files_dir / "metadata=long a_id3v1_big.wav"


# Test tracks with ID3v2 metadata
@pytest.fixture
def metadata_id3v2_small_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with ID3v2 metadata (small)."""
    return test_files_dir / "metadata=long a_id3v2_small.mp3"


@pytest.fixture
def metadata_id3v2_big_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with ID3v2 metadata (big)."""
    return test_files_dir / "metadata=long a_id3v2_big.mp3"


@pytest.fixture
def metadata_id3v2_small_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with ID3v2 metadata (small)."""
    return test_files_dir / "metadata=long a_id3v2_small.flac"


@pytest.fixture
def metadata_id3v2_big_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with ID3v2 metadata (big)."""
    return test_files_dir / "metadata=long a_id3v2_big.flac"


@pytest.fixture
def metadata_id3v2_small_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with ID3v2 metadata (small)."""
    return test_files_dir / "metadata=long a_id3v2_small.wav"


@pytest.fixture
def metadata_id3v2_big_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with ID3v2 metadata (big)."""
    return test_files_dir / "metadata=long a_id3v2_big.wav"


@pytest.fixture
def metadata_id3v2_and_riff_small_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with both ID3v2 and RIFF metadata (small)."""
    return test_files_dir / "metadata=long a_id3v2_and_riff_small.wav"


# Test tracks with RIFF metadata
@pytest.fixture
def metadata_riff_small_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with RIFF metadata (small)."""
    return test_files_dir / "metadata=long a_riff_small.wav"


@pytest.fixture
def metadata_riff_big_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with RIFF metadata (big)."""
    return test_files_dir / "metadata=long a_riff_big.wav"


# Test tracks with Vorbis metadata
@pytest.fixture
def metadata_vorbis_small_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with Vorbis metadata (small)."""
    return test_files_dir / "metadata=long a_vorbis_small.flac"


@pytest.fixture
def metadata_vorbis_big_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with Vorbis metadata (big)."""
    return test_files_dir / "metadata=long a_vorbis_big.flac"


# Rating test tracks - ID3v2 base 100
@pytest.fixture
def rating_id3v2_base_100_0_star_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with ID3v2 rating 0 star (base 100)."""
    return test_files_dir / "rating_id3v2_base 100=0 star.wav"


@pytest.fixture
def rating_id3v2_base_100_5_star_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with ID3v2 rating 5 star (base 100)."""
    return test_files_dir / "rating_id3v2_base 100=5 star.wav"


# Rating test tracks - ID3v2 base 255
@pytest.fixture
def rating_id3v2_base_255_5_star_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with ID3v2 rating 5 star (base 255)."""
    return test_files_dir / "rating_id3v2_base 255_kid3=5 star.mp3"


# Rating test tracks - RIFF base 100
@pytest.fixture
def rating_riff_base_100_5_star_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with RIFF rating 5 star (base 100)."""
    return test_files_dir / "rating_riff_base 100_kid3=5 star.wav"


# Rating test tracks - Vorbis base 100
@pytest.fixture
def rating_vorbis_base_100_5_star_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with Vorbis rating 5 star (base 100)."""
    return test_files_dir / "rating_vorbis=5 star.flac"


# Artist test tracks
@pytest.fixture
def artists_one_two_three_comma_id3v2(test_files_dir: Path) -> Path:
    """Return path to MP3 file with artists 'One Two Three' (comma separated)."""
    return test_files_dir / "artists=One Two Three_comma_id3v2.mp3"


@pytest.fixture
def artists_one_two_three_semicolon_id3v2(test_files_dir: Path) -> Path:
    """Return path to MP3 file with artists 'One Two Three' (semicolon separated)."""
    return test_files_dir / "artists=One Two Three_semicolon_id3v2.mp3"


@pytest.fixture
def artists_one_two_three_multi_tags_vorbis(test_files_dir: Path) -> Path:
    """Return path to FLAC file with artists 'One Two Three' (multi tags vorbis)."""
    return test_files_dir / "artists=One Two Three_muti tags_vorbis.flac"


# Album test tracks
@pytest.fixture
def album_koko_id3v2_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with album 'koko' (ID3v2)."""
    return test_files_dir / "album=koko_id3v2.mp3"


@pytest.fixture
def album_koko_id3v2_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with album 'koko' (ID3v2)."""
    return test_files_dir / "album=koko_id3v2.wav"


@pytest.fixture
def album_koko_vorbis_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with album 'koko' (Vorbis)."""
    return test_files_dir / "album=koko_vorbis.flac"


# Genre test tracks
@pytest.fixture
def genre_code_id3v1_abstract_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with ID3v1 genre code 'Abstract'."""
    return test_files_dir / "genre_code_id3v1=Abstract.mp3"


@pytest.fixture
def genre_code_id3v1_unknown_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with ID3v1 genre code 'Unknown'."""
    return test_files_dir / "genre_code_id3v1=Unknown.mp3"


# Duration test tracks
@pytest.fixture
def duration_1s_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with 1 second duration."""
    return test_files_dir / "duration=1s.wav"


@pytest.fixture
def duration_182s_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with 182 seconds duration."""
    return test_files_dir / "duration=182.mp3"


@pytest.fixture
def duration_335s_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with 335 seconds duration."""
    return test_files_dir / "duration=335s.flac"


@pytest.fixture
def duration_472s_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with 472 seconds duration."""
    return test_files_dir / "duration=472s.wav"


# Bitrate test tracks
@pytest.fixture
def bitrate_320_mp3(test_files_dir: Path) -> Path:
    """Return path to MP3 file with 320 kbps bitrate."""
    return test_files_dir / "bitrate in kbps_big=320.mp3"


@pytest.fixture
def bitrate_946_flac(test_files_dir: Path) -> Path:
    """Return path to FLAC file with 946 kbps bitrate."""
    return test_files_dir / "bitrate in kbps_big=946.flac"


@pytest.fixture
def bitrate_1411_wav(test_files_dir: Path) -> Path:
    """Return path to WAV file with 1411 kbps bitrate."""
    return test_files_dir / "bitrate in kbps_big=1411.wav"


# Size test tracks
@pytest.fixture
def size_small_mp3(test_files_dir: Path) -> Path:
    """Return path to small MP3 file (0.01 MB)."""
    return test_files_dir / "size_small=0.01mo.mp3"


@pytest.fixture
def size_big_mp3(test_files_dir: Path) -> Path:
    """Return path to big MP3 file (9.98 MB)."""
    return test_files_dir / "size_big=9.98mo.mp3"


@pytest.fixture
def size_small_flac(test_files_dir: Path) -> Path:
    """Return path to small FLAC file (0.05 MB)."""
    return test_files_dir / "size_small=0.05mo.flac"


@pytest.fixture
def size_big_flac(test_files_dir: Path) -> Path:
    """Return path to big FLAC file (26.6 MB)."""
    return test_files_dir / "size_big=26.6mo.flac"


@pytest.fixture
def size_small_wav(test_files_dir: Path) -> Path:
    """Return path to small WAV file (0.08 MB)."""
    return test_files_dir / "size_small=0.08mo.wav"


@pytest.fixture
def size_big_wav(test_files_dir: Path) -> Path:
    """Return path to big WAV file (79.55 MB)."""
    return test_files_dir / "size_big=79.55mo.wav"