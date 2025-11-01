import pytest

from audiometa import AudioFile, get_duration_in_sec
from audiometa.exceptions import FileByteMismatchError, FileCorruptedError


@pytest.mark.integration
class TestTechnicalInfoErrorHandling:

    def test_file_byte_mismatch_error_corrupted_flac(self, tmp_path):
        corrupted_flac = tmp_path / "corrupted.flac"
        corrupted_flac.write_bytes(b"fake file")
        
        try:
            audio_file = AudioFile(corrupted_flac)
            audio_file.get_duration_in_sec()
            pytest.fail("Should have raised FileByteMismatchError or FileCorruptedError")
        except (FileByteMismatchError, FileCorruptedError):
            pass

    def test_file_corrupted_error_invalid_wav(self, tmp_path):
        invalid_wav = tmp_path / "invalid.wav"
        invalid_wav.write_bytes(b"not a valid wav file")
        
        try:
            get_duration_in_sec(invalid_wav)
            pytest.fail("Should have raised FileCorruptedError")
        except (FileCorruptedError, RuntimeError):
            pass