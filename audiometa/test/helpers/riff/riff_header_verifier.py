"""RIFF metadata header verification utilities."""

from pathlib import Path

from ..common.external_tool_runner import run_external_tool


class RIFFHeaderVerifier:
    """Utilities for verifying RIFF metadata headers in audio files."""

    @staticmethod
    def has_riff_info_chunk(file_path: Path) -> bool:
        """Check if file has RIFF INFO chunk by reading file structure."""
        try:
            with file_path.open("rb") as f:
                # Read first few bytes to check for ID3v2 tags
                first_bytes = f.read(10)
                f.seek(0)  # Reset to beginning

                if first_bytes.startswith(b"ID3"):
                    # File has ID3v2 tags, find RIFF header after them
                    data = f.read()
                    pos = 0
                    while pos < len(data) - 8:
                        if data[pos : pos + 4] == b"RIFF":
                            # Found RIFF header, check for LIST chunk containing INFO
                            riff_size = int.from_bytes(data[pos + 4 : pos + 8], "little")
                            riff_data = data[pos + 8 : pos + 8 + riff_size]

                            # Search for LIST chunk containing INFO in RIFF data
                            # Skip the WAVE chunk header (4 bytes)
                            info_pos = 4
                            while info_pos < len(riff_data) - 8:
                                chunk_id = riff_data[info_pos : info_pos + 4]
                                chunk_size = int.from_bytes(riff_data[info_pos + 4 : info_pos + 8], "little")

                                if chunk_id == b"LIST":
                                    # Check if this LIST chunk contains INFO
                                    list_data = riff_data[info_pos + 8 : info_pos + 8 + chunk_size]
                                    if len(list_data) >= 4 and list_data[:4] == b"INFO":
                                        return True

                                # Move to next chunk (chunk size + padding)
                                info_pos += 8 + chunk_size
                                if chunk_size % 2 == 1:  # Odd size needs padding
                                    info_pos += 1
                            return False
                        pos += 1
                    return False
                # File starts with RIFF header
                riff_header = f.read(12)
                if riff_header[:4] != b"RIFF":
                    return False

                # Look for LIST chunk containing INFO
                chunk_size = int.from_bytes(riff_header[4:8], "little")
                data = f.read(chunk_size)

                # Search for LIST chunk containing INFO
                pos = 0
                while pos < len(data) - 8:
                    chunk_id = data[pos : pos + 4]
                    chunk_size = int.from_bytes(data[pos + 4 : pos + 8], "little")

                    if chunk_id == b"LIST":
                        # Check if this LIST chunk contains INFO
                        list_data = data[pos + 8 : pos + 8 + chunk_size]
                        if len(list_data) >= 4 and list_data[:4] == b"INFO":
                            return True

                    # Move to next chunk (chunk size + padding)
                    pos += 8 + chunk_size
                    if chunk_size % 2 == 1:  # Odd size needs padding
                        pos += 1

                return False
        except (OSError, ValueError):
            return False

    @staticmethod
    def get_riff_metadata_info(file_path: Path) -> str:
        """Get RIFF metadata info using exiftool."""
        command = ["exiftool", "-a", "-G", str(file_path)]
        result = run_external_tool(command, "exiftool")
        return result.stdout
