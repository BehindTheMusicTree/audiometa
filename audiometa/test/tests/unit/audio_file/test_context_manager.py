import pytest
from pathlib import Path
from unittest.mock import patch

from audiometa import AudioFile


@pytest.mark.unit
class TestAudioFileOperations:

    def test_context_manager(self, sample_mp3_file: Path):
        with patch('audiometa.AudioFile.close') as mock_close:
            with AudioFile(sample_mp3_file) as audio_file:
                # Ensure __enter__ returns the AudioFile instance
                assert isinstance(audio_file, AudioFile)
                assert audio_file.file_path == str(sample_mp3_file)
                
                # Optionally, perform an operation inside the context to ensure it's functional
                # (e.g., check that methods work without issues)
                duration = audio_file.get_duration_in_sec()
                assert duration > 0  # Or some basic validation
            
            # After exiting, verify that close was called
            mock_close.assert_called_once()