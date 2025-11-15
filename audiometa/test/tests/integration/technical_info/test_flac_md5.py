import subprocess
import tempfile
from pathlib import Path

import pytest

from audiometa import fix_md5_checking, is_flac_md5_valid
from audiometa.exceptions import FileTypeNotSupportedError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


def _ensure_flac_has_md5(file_path: Path) -> None:
    """Re-encode FLAC file to ensure MD5 signature is set."""
    with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as temp_flac:
        temp_flac_path = temp_flac.name

    try:
        subprocess.run(
            ["flac", "-f", "--best", "-o", temp_flac_path, str(file_path)],
            capture_output=True,
            check=True,
        )
        Path(temp_flac_path).replace(file_path)
    except Exception:
        if Path(temp_flac_path).exists():
            Path(temp_flac_path).unlink()
        raise


def _get_md5_position(file_path: Path) -> int:
    """Get the byte position of the MD5 checksum in the STREAMINFO block."""
    with file_path.open("rb") as f:
        data = f.read()
        flac_marker_pos = data.find(b"fLaC")
        if flac_marker_pos == -1:
            msg = "Could not find FLAC marker in file"
            raise RuntimeError(msg)
        md5_start = flac_marker_pos + 4 + 1 + 18
        if md5_start + 16 > len(data):
            msg = "FLAC file too small to contain MD5 checksum"
            raise RuntimeError(msg)
        return md5_start


def _corrupt_md5(file_path: Path, corruption_type: str = "flip_all") -> None:
    """Corrupt the MD5 checksum in a FLAC file.

    Args:
        file_path: Path to FLAC file
        corruption_type: Type of corruption:
            - "flip_all": Flip all bits (XOR 0xFF)
            - "partial": Corrupt only first 4 bytes
            - "zeros": Set MD5 to all zeros (unset)
            - "random": Set MD5 to a random but valid-looking value
    """
    md5_start = _get_md5_position(file_path)

    with file_path.open("r+b") as f:
        f.seek(md5_start)
        original_md5 = f.read(16)

        if corruption_type == "flip_all":
            corrupted_md5 = bytes(b ^ 0xFF for b in original_md5)
        elif corruption_type == "partial":
            corrupted_md5 = bytes(b ^ 0xFF for b in original_md5[:4]) + original_md5[4:]
        elif corruption_type == "zeros":
            corrupted_md5 = b"\x00" * 16
        elif corruption_type == "random":
            corrupted_md5 = b"\x12\x34\x56\x78" * 4
        else:
            msg = f"Unknown corruption type: {corruption_type}"
            raise ValueError(msg)

        f.seek(md5_start)
        f.write(corrupted_md5)


@pytest.mark.integration
class TestFlacMd5Functions:
    def test_is_flac_md5_valid_works_with_path_string(self, sample_flac_file: Path):
        is_valid = is_flac_md5_valid(str(sample_flac_file))
        assert isinstance(is_valid, bool)

    def test_is_flac_md5_valid_works_with_pathlib_path(self, sample_flac_file: Path):
        is_valid = is_flac_md5_valid(sample_flac_file)
        assert isinstance(is_valid, bool)

    def test_is_flac_md5_valid_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            is_flac_md5_valid(sample_mp3_file)

    def test_fix_md5_checking_flac(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            _ensure_flac_has_md5(test_file)
            _corrupt_md5(test_file, "flip_all")

            assert not is_flac_md5_valid(test_file), "Test file should have invalid MD5 for fix_md5_checking test"

            fixed_file_path = fix_md5_checking(test_file)
            assert is_flac_md5_valid(fixed_file_path), "Fixed file should have valid MD5"

            Path(fixed_file_path).unlink()

    def test_is_flac_md5_valid_detects_flipped_md5(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            _ensure_flac_has_md5(test_file)
            _corrupt_md5(test_file, "flip_all")

            assert not is_flac_md5_valid(test_file), "Flipped MD5 should be detected as invalid"

    def test_is_flac_md5_valid_detects_partial_md5_corruption(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            _ensure_flac_has_md5(test_file)
            _corrupt_md5(test_file, "partial")

            assert not is_flac_md5_valid(test_file), "Partially corrupted MD5 should be detected as invalid"

    def test_is_flac_md5_valid_detects_random_md5_corruption(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            _ensure_flac_has_md5(test_file)
            _corrupt_md5(test_file, "random")

            assert not is_flac_md5_valid(test_file), "Random MD5 corruption should be detected as invalid"

    def test_is_flac_md5_valid_with_unset_md5(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            _ensure_flac_has_md5(test_file)
            _corrupt_md5(test_file, "zeros")

            # Unset MD5 (all zeros) may or may not be detected as invalid depending on flac version
            # Some versions of flac report this as valid, others as invalid
            result = is_flac_md5_valid(test_file)
            assert isinstance(result, bool), "Should return a boolean value"

    def test_fix_md5_checking_with_partial_corruption(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            _ensure_flac_has_md5(test_file)
            _corrupt_md5(test_file, "partial")

            assert not is_flac_md5_valid(test_file), "Partially corrupted MD5 should be invalid"

            fixed_file_path = fix_md5_checking(test_file)
            assert is_flac_md5_valid(fixed_file_path), "Fixed file should have valid MD5"

            Path(fixed_file_path).unlink()

    def test_fix_md5_checking_with_random_corruption(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            _ensure_flac_has_md5(test_file)
            _corrupt_md5(test_file, "random")

            assert not is_flac_md5_valid(test_file), "Random MD5 corruption should be invalid"

            fixed_file_path = fix_md5_checking(test_file)
            assert is_flac_md5_valid(fixed_file_path), "Fixed file should have valid MD5"

            Path(fixed_file_path).unlink()

    def test_is_flac_md5_valid_with_audio_data_corruption(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            _ensure_flac_has_md5(test_file)

            # Corrupt audio data in the middle of the file (not MD5)
            file_size = test_file.stat().st_size
            with test_file.open("r+b") as f:
                corrupt_position = max(1000, file_size // 2)
                f.seek(corrupt_position)
                original_bytes = f.read(100)
                f.seek(corrupt_position)
                corrupted_bytes = bytes(b ^ 0xFF for b in original_bytes)
                f.write(corrupted_bytes)

            # Audio data corruption should invalidate MD5
            assert not is_flac_md5_valid(test_file), "Audio data corruption should invalidate MD5"

    def test_fix_md5_checking_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            fix_md5_checking(sample_mp3_file)
