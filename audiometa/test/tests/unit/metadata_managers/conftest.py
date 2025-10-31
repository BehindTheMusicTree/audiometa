import pytest
from unittest.mock import MagicMock

from audiometa import AudioFile


@pytest.fixture
def mock_audio_file_mp3():
    mock_audio_file = MagicMock(spec=AudioFile)
    mock_audio_file.file_path = "/path/to/test.mp3"
    mock_audio_file.file_extension = ".mp3"
    return mock_audio_file


@pytest.fixture
def mock_audio_file_wav():
    mock_audio_file = MagicMock(spec=AudioFile)
    mock_audio_file.file_path = "/path/to/test.wav"
    mock_audio_file.file_extension = ".wav"
    return mock_audio_file


@pytest.fixture
def mock_audio_file_flac():
    mock_audio_file = MagicMock(spec=AudioFile)
    mock_audio_file.file_path = "/path/to/test.flac"
    mock_audio_file.file_extension = ".flac"
    return mock_audio_file


@pytest.fixture
def mock_id3_empty():
    mock_id3 = MagicMock()
    mock_id3.version = (2, 3, 0)
    mock_id3.size = 0
    mock_id3.flags = 0
    mock_id3.__contains__ = lambda key: False
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
        'TIT2': mock_title,
        'TPE1': mock_artists,
        'TALB': mock_album,
    }
    
    mock_id3.__contains__ = lambda key: key in frame_dict
    mock_id3.__getitem__ = lambda key: frame_dict.get(key)
    mock_id3.items.return_value = []
    
    return mock_id3


@pytest.fixture
def mock_id3_with_header_info():
    mock_id3 = MagicMock()
    mock_id3.version = (2, 3, 0)
    mock_id3.size = 2048
    mock_id3.flags = 0x40
    mock_id3.__contains__ = lambda key: False
    mock_id3.items.return_value = []
    
    mock_extended_header = MagicMock()
    mock_extended_header.size = 512
    mock_extended_header.flags = 0x00
    mock_extended_header.padding_size = 256
    mock_id3.extended_header = mock_extended_header
    
    return mock_id3

