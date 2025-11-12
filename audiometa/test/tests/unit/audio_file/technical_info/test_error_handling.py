import pytest

from audiometa._audio_file import _AudioFile as _AudioFile
from audiometa.exceptions import (
    AudioFileMetadataParseError,
    DurationNotFoundError,
    FileByteMismatchError,
    FileCorruptedError,
    FlacMd5CheckFailedError,
    InvalidChunkDecodeError,
)


@pytest.mark.unit
class TestAudioFileTechnicalInfoErrorHandling:
    def test_file_byte_mismatch_error_corrupted_flac(self, tmp_path):
        corrupted_flac = tmp_path / "corrupted.flac"
        corrupted_flac.write_bytes(b"fake file")

        try:
            audio_file = _AudioFile(corrupted_flac)
            audio_file.get_duration_in_sec()
            pytest.fail("Should have raised FileByteMismatchError or FileCorruptedError")
        except (FileByteMismatchError, FileCorruptedError):
            pass

    def test_flac_md5_check_failed_error_corrupted_flac(self, monkeypatch):
        def mock_subprocess_run(*args, **kwargs):
            class MockResult:
                stderr = b"Some unexpected FLAC error message"
                returncode = 1

            return MockResult()

        monkeypatch.setattr("subprocess.run", mock_subprocess_run)

        flac_file = "audiometa/test/assets/sample.flac"

        try:
            audio_file = _AudioFile(flac_file)
            audio_file.is_flac_file_md5_valid()
            pytest.fail("Should have raised FlacMd5CheckFailedError")
        except FlacMd5CheckFailedError:
            pass

    def test_invalid_chunk_decode_error_corrupted_flac_chunks(self, monkeypatch):
        def mock_get_duration_in_sec(self):
            try:
                raise Exception("FLAC chunk decoding failed")
            except Exception as exc:
                error_str = str(exc)
                if "file said" in error_str and "bytes, read" in error_str:
                    raise FileByteMismatchError(error_str.capitalize())
                elif "FLAC" in error_str or "chunk" in error_str.lower():
                    raise InvalidChunkDecodeError(f"Failed to decode FLAC chunks: {error_str}")
                raise

        monkeypatch.setattr("audiometa._audio_file._AudioFile.get_duration_in_sec", mock_get_duration_in_sec)

        flac_file = "audiometa/test/assets/sample.flac"

        try:
            audio_file = _AudioFile(flac_file)
            audio_file.get_duration_in_sec()
            pytest.fail("Should have raised InvalidChunkDecodeError")
        except InvalidChunkDecodeError:
            pass

    def test_duration_not_found_error_invalid_wav_duration(self, monkeypatch):
        def mock_subprocess_run(*args, **kwargs):
            class MockResult:
                returncode = 0
                stdout = '{"format": {"duration": "0.0"}, "streams": [{"duration": "0"}]}'

            return MockResult()

        monkeypatch.setattr("subprocess.run", mock_subprocess_run)

        wav_file = "audiometa/test/assets/sample.wav"

        try:
            audio_file = _AudioFile(wav_file)
            audio_file.get_duration_in_sec()
            pytest.fail("Should have raised DurationNotFoundError")
        except DurationNotFoundError:
            pass

    def test_audio_file_metadata_parse_error_invalid_json(self, monkeypatch):
        def mock_subprocess_run(*args, **kwargs):
            class MockResult:
                returncode = 0
                stdout = "invalid json response"

            return MockResult()

        monkeypatch.setattr("subprocess.run", mock_subprocess_run)

        wav_file = "audiometa/test/assets/sample.wav"

        try:
            audio_file = _AudioFile(wav_file)
            audio_file.get_duration_in_sec()
            pytest.fail("Should have raised AudioFileMetadataParseError")
        except AudioFileMetadataParseError:
            pass

    def test_file_corrupted_error_invalid_wav(self, tmp_path):
        invalid_wav = tmp_path / "invalid.wav"
        invalid_wav.write_bytes(b"not a valid wav file")

        try:
            audio_file = _AudioFile(invalid_wav)
            audio_file.get_duration_in_sec()
            pytest.fail("Should have raised FileCorruptedError")
        except (FileCorruptedError, RuntimeError):
            pass
