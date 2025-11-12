"""ID3v1 metadata header verification utilities."""

from pathlib import Path


class ID3v1HeaderVerifier:
    """Utilities for verifying ID3v1 metadata headers in audio files."""

    @staticmethod
    def has_id3v1_header(file_path: Path) -> bool:
        """Check if file has ID3v1 header by reading the last 128 bytes."""
        try:
            with file_path.open("rb") as f:
                f.seek(-128, 2)  # Seek to last 128 bytes
                header = f.read(128)
                return header[:3] == b"TAG"
        except OSError:
            return False
