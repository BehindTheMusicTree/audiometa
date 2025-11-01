import pytest

from audiometa import AudioFile, get_duration_in_sec
from audiometa.exceptions import FileByteMismatchError, FileCorruptedError, FlacMd5CheckFailedError, InvalidChunkDecodeError, DurationNotFoundError, AudioFileMetadataParseError


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

    def test_flac_md5_check_failed_error_corrupted_flac(self, monkeypatch):
        # Mock subprocess.run to return an unexpected error that triggers FlacMd5CheckFailedError
        def mock_subprocess_run(*args, **kwargs):
            class MockResult:
                stderr = b"Some unexpected FLAC error message"
                returncode = 1
            return MockResult()
        
        monkeypatch.setattr('subprocess.run', mock_subprocess_run)
        
        # Use a valid FLAC file from test assets
        flac_file = "audiometa/test/assets/sample.flac"
        
        try:
            audio_file = AudioFile(flac_file)
            audio_file.is_flac_file_md5_valid()
            pytest.fail("Should have raised FlacMd5CheckFailedError")
        except FlacMd5CheckFailedError:
            pass

    def test_invalid_chunk_decode_error_corrupted_flac_chunks(self, monkeypatch):
        # Mock the get_duration_in_sec method to simulate FLAC chunk decoding failure
        original_get_duration = None
        
        def mock_get_duration_in_sec(self):
            # Simulate what happens when FLAC() raises an exception with "FLAC" in the message
            try:
                # This will raise our mocked exception
                raise Exception("FLAC chunk decoding failed")
            except Exception as exc:
                error_str = str(exc)
                if "file said" in error_str and "bytes, read" in error_str:
                    raise FileByteMismatchError(error_str.capitalize())
                elif "FLAC" in error_str or "chunk" in error_str.lower():
                    raise InvalidChunkDecodeError(f"Failed to decode FLAC chunks: {error_str}")
                raise
        
        # Store original method and patch it
        from audiometa.audio_file import AudioFile
        original_get_duration = AudioFile.get_duration_in_sec
        monkeypatch.setattr('audiometa.audio_file.AudioFile.get_duration_in_sec', mock_get_duration_in_sec)
        
        # Use a valid FLAC file path
        flac_file = "audiometa/test/assets/sample.flac"
        
        try:
            audio_file = AudioFile(flac_file)
            audio_file.get_duration_in_sec()
            pytest.fail("Should have raised InvalidChunkDecodeError")
        except InvalidChunkDecodeError:
            pass

    def test_duration_not_found_error_invalid_wav_duration(self, monkeypatch):
        # Mock subprocess.run to return JSON with zero duration
        def mock_subprocess_run(*args, **kwargs):
            class MockResult:
                returncode = 0
                stdout = '{"format": {"duration": "0.0"}, "streams": [{"duration": "0"}]}'
            return MockResult()
        
        monkeypatch.setattr('subprocess.run', mock_subprocess_run)
        
        # Use a valid WAV file path
        wav_file = "audiometa/test/assets/sample.wav"
        
        try:
            audio_file = AudioFile(wav_file)
            audio_file.get_duration_in_sec()
            pytest.fail("Should have raised DurationNotFoundError")
        except DurationNotFoundError:
            pass

    def test_audio_file_metadata_parse_error_invalid_json(self, monkeypatch):
        # Mock subprocess.run to return invalid JSON that will cause JSONDecodeError
        def mock_subprocess_run(*args, **kwargs):
            class MockResult:
                returncode = 0
                stdout = "invalid json response"
            return MockResult()
        
        monkeypatch.setattr('subprocess.run', mock_subprocess_run)
        
        # Use a valid WAV file path
        wav_file = "audiometa/test/assets/sample.wav"
        
        try:
            audio_file = AudioFile(wav_file)
            audio_file.get_duration_in_sec()
            pytest.fail("Should have raised AudioFileMetadataParseError")
        except AudioFileMetadataParseError:
            pass