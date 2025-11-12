from unittest.mock import MagicMock

import pytest

from audiometa._audio_file import _AudioFile


@pytest.fixture
def mock_audio_file_mp3():
    mock_audio_file = MagicMock(spec=_AudioFile)
    mock_audio_file.file_path = "/path/to/test.mp3"
    mock_audio_file.file_extension = ".mp3"
    return mock_audio_file


@pytest.fixture
def mock_audio_file_wav():
    mock_audio_file = MagicMock(spec=_AudioFile)
    mock_audio_file.file_path = "/path/to/test.wav"
    mock_audio_file.file_extension = ".wav"
    return mock_audio_file


@pytest.fixture
def mock_audio_file_flac():
    mock_audio_file = MagicMock(spec=_AudioFile)
    mock_audio_file.file_path = "/path/to/test.flac"
    mock_audio_file.file_extension = ".flac"
    return mock_audio_file


@pytest.fixture
def mock_id3_empty():
    mock_id3 = MagicMock()
    mock_id3.version = (2, 3, 0)
    mock_id3.size = 0
    mock_id3.flags = 0
    mock_id3.__contains__ = lambda _self, _key: False
    mock_id3.items.return_value = []
    mock_id3.extended_header = None
    return mock_id3


@pytest.fixture
def mock_id3_with_metadata():
    mock_id3 = MagicMock()
    mock_id3.version = (2, 3, 0)
    mock_id3.size = 2048
    mock_id3.flags = 0x40
    mock_id3.extended_header = None

    mock_title = MagicMock()
    mock_title.text = ["Test Title"]
    mock_artists = MagicMock()
    mock_artists.text = ["Test Artist"]
    mock_album = MagicMock()
    mock_album.text = ["Test Album"]

    frame_dict = {
        "TIT2": mock_title,
        "TPE1": mock_artists,
        "TALB": mock_album,
    }

    mock_id3.__contains__ = lambda _self, key: key in frame_dict
    mock_id3.__getitem__ = lambda _self, key: frame_dict.get(key)
    mock_id3.items.return_value = []

    return mock_id3


@pytest.fixture
def mock_id3_updatable():
    """Mock ID3 object that supports add/delall operations for update_metadata testing."""
    mock_id3 = MagicMock()
    mock_id3.version = (2, 3, 0)
    mock_id3.size = 0
    mock_id3.flags = 0
    mock_id3.extended_header = None

    # Storage for frames
    frames = {}

    def mock_delall(key):
        """Remove all frames with the given key."""
        keys_to_remove = [k for k in frames if k.startswith(key)]
        for k in keys_to_remove:
            del frames[k]

    def mock_add(frame):
        """Add a frame to the mock."""
        frame_id = frame.FrameID
        if hasattr(frame, "email"):  # POPM frame
            frame_id = f"{frame_id}:{frame.email}"

        frames[frame_id] = frame

    def mock_items():
        """Return list of (key, frame) tuples."""
        return list(frames.items())

    mock_id3.delall = mock_delall
    mock_id3.add = mock_add
    mock_id3.items = mock_items
    mock_id3.__contains__ = lambda _self, key: key in frames
    mock_id3.__getitem__ = lambda _self, key: frames[key]

    return mock_id3


@pytest.fixture
def mock_wave_empty():
    mock_wave = MagicMock()
    mock_wave.info = {}
    return mock_wave


@pytest.fixture
def mock_wave_with_metadata():
    mock_wave = MagicMock()
    mock_wave.info = {
        "INAM": ["Test Title"],
        "IART": ["Test Artist"],
        "IPRD": ["Test Album"],
    }
    return mock_wave


@pytest.fixture
def mock_vorbis_metadata_empty():
    """Mock Vorbis metadata dict with no metadata."""
    return {}


@pytest.fixture
def mock_vorbis_metadata_with_data():
    """Mock Vorbis metadata dict with sample metadata."""
    return {
        "TITLE": ["Test Title"],
        "ARTIST": ["Test Artist"],
        "ALBUM": ["Test Album"],
    }
