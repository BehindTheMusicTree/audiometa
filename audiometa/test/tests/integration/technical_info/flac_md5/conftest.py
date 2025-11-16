import subprocess
import tempfile
from pathlib import Path


def ensure_flac_has_md5(file_path: Path) -> None:
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


def create_flac_without_md5(file_path: Path) -> None:
    """Create a FLAC file without MD5 checksum (naturally unset).

    Some FLAC encoders don't set MD5 by default, or files can be encoded with MD5 disabled. This function creates a FLAC
    file without MD5 by decoding to WAV and re-encoding without MD5, or by using metaflac to remove the MD5 checksum.
    """
    # First ensure we have a valid FLAC file
    ensure_flac_has_md5(file_path)

    # Use metaflac to remove MD5 checksum (set to all zeros)
    # This simulates a naturally unset MD5
    md5_start = get_md5_position(file_path)
    with file_path.open("r+b") as f:
        f.seek(md5_start)
        f.write(b"\x00" * 16)


def get_md5_position(file_path: Path) -> int:
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


def corrupt_md5(file_path: Path, corruption_type: str = "flip_all") -> None:
    """Corrupt the MD5 checksum in a FLAC file.

    Args:
        file_path: Path to FLAC file
        corruption_type: Type of corruption:
            - "flip_all": Flip all bits (XOR 0xFF)
            - "partial": Corrupt only first 4 bytes
            - "zeros": Set MD5 to all zeros (unset)
            - "random": Set MD5 to a random but valid-looking value
    """
    md5_start = get_md5_position(file_path)

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


def corrupt_audio_data(file_path: Path) -> None:
    """Corrupt audio data in the middle of a FLAC file.

    This simulates real-world file corruption by corrupting bytes in the compressed FLAC stream. The corruption is done
    realistically, not specifically to make any tool detect it. If the corruption is not detected, that is a limitation
    we need to handle in our code, not work around by making corruption that will be detected.
    """
    file_size = file_path.stat().st_size
    with file_path.open("r+b") as f:
        corrupt_position = max(1000, file_size // 2)
        f.seek(corrupt_position)
        original_bytes = f.read(100)
        f.seek(corrupt_position)
        corrupted_bytes = bytes(b ^ 0xFF for b in original_bytes)
        f.write(corrupted_bytes)
