import pytest

from audiometa._audio_file import _AudioFile
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.unit
class TestAudioFileOperations:
    def test_file_operations(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            audio_file = _AudioFile(test_file)

            # Test write
            test_data = b"test audio data"
            bytes_written = audio_file.write(test_data)
            assert bytes_written == len(test_data)

            # Test read
            read_data = audio_file.read()
            assert read_data == test_data
