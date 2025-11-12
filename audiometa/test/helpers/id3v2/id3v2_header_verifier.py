"""ID3 metadata header verification utilities."""

from pathlib import Path


class ID3v2HeaderVerifier:
    """Utilities for verifying ID3 metadata headers in audio files."""

    @staticmethod
    def has_id3v2_header(file_path: Path) -> bool:
        """Check if file has ID3v2 header by reading the first 10 bytes."""
        try:
            with file_path.open("rb") as f:
                header = f.read(10)
                return header[:3] == b"ID3"
        except OSError:
            return False

    @staticmethod
    def get_id3v2_version(file_path: Path) -> tuple[int, int, int] | None:
        """Get the ID3v2 version of the file.

        Args:
            file_path: Path to the audio file

        Returns:
            Version tuple (major, minor, revision) or None if no ID3v2 header found
        """
        try:
            from mutagen.id3 import ID3, ID3NoHeaderError

            id3_tags = ID3(file_path)
        except ID3NoHeaderError:
            return None
        except Exception:
            return None
        else:
            return id3_tags.version
