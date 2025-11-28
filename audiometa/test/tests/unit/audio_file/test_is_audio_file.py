from pathlib import Path

import pytest

from audiometa import is_audio_file


@pytest.mark.unit
class TestIsAudioFile:
    def test_valid_mp3_file_returns_true(self, sample_mp3_file: Path):
        assert is_audio_file(sample_mp3_file) is True
        assert is_audio_file(str(sample_mp3_file)) is True

    def test_valid_flac_file_returns_true(self, sample_flac_file: Path):
        assert is_audio_file(sample_flac_file) is True
        assert is_audio_file(str(sample_flac_file)) is True

    def test_valid_wav_file_returns_true(self, sample_wav_file: Path):
        assert is_audio_file(sample_wav_file) is True
        assert is_audio_file(str(sample_wav_file)) is True

    def test_nonexistent_file_returns_false(self):
        assert is_audio_file("nonexistent.mp3") is False
        assert is_audio_file(Path("nonexistent.flac")) is False

    def test_unsupported_extension_returns_false(self, sample_m4a_file: Path):
        assert is_audio_file(sample_m4a_file) is False
        assert is_audio_file(str(sample_m4a_file)) is False

    def test_invalid_mp3_content_returns_false(self, tmp_path: Path):
        invalid_mp3 = tmp_path / "invalid.mp3"
        invalid_mp3.write_bytes(b"not a real audio file")

        assert is_audio_file(invalid_mp3) is False
        assert is_audio_file(str(invalid_mp3)) is False

    def test_invalid_flac_content_returns_false(self, tmp_path: Path):
        invalid_flac = tmp_path / "invalid.flac"
        invalid_flac.write_bytes(b"not a real audio file")

        assert is_audio_file(invalid_flac) is False
        assert is_audio_file(str(invalid_flac)) is False

    def test_invalid_wav_content_returns_false(self, tmp_path: Path):
        invalid_wav = tmp_path / "invalid.wav"
        invalid_wav.write_bytes(b"not a real audio file")

        assert is_audio_file(invalid_wav) is False
        assert is_audio_file(str(invalid_wav)) is False
