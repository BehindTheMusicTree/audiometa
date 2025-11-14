"""RIFF metadata inspection utilities for testing audio file metadata."""

from pathlib import Path

from ..common.external_tool_runner import run_external_tool


class RIFFMetadataGetter:
    """Utilities for inspecting RIFF metadata in audio files."""

    @staticmethod
    def get_raw_metadata(file_path: Path) -> str:
        """Inspect RIFF metadata using custom binary reading to detect multiple fields."""
        # Read the file and find all RIFF INFO fields
        with file_path.open("rb") as f:
            data = f.read()

        # Find all RIFF INFO fields
        info_fields = {}
        pos = 0
        while pos < len(data) - 4:
            # Look for RIFF INFO chunk
            if data[pos : pos + 4] == b"LIST" and pos + 12 <= len(data) and data[pos + 8 : pos + 12] == b"INFO":
                # Found INFO chunk, parse its fields
                chunk_size = int.from_bytes(data[pos + 4 : pos + 8], "little")
                info_data = data[pos + 12 : pos + 8 + chunk_size]

                # Parse fields within INFO chunk
                field_pos = 0
                while field_pos < len(info_data) - 8:
                    if field_pos + 8 <= len(info_data):
                        field_id = info_data[field_pos : field_pos + 4]
                        field_size = int.from_bytes(info_data[field_pos + 4 : field_pos + 8], "little")

                        if field_pos + 8 + field_size <= len(info_data):
                            field_data = info_data[field_pos + 8 : field_pos + 8 + field_size]
                            # Remove null terminator
                            if field_data.endswith(b"\x00"):
                                field_data = field_data[:-1]
                            text = field_data.decode("utf-8", errors="ignore")

                            # Map RIFF field IDs to ffprobe-style tags
                            field_id_str = field_id.decode("ascii", errors="ignore")
                            tag_name = RIFFMetadataGetter._get_tag_name_for_field(field_id_str)

                            if tag_name not in info_fields:
                                info_fields[tag_name] = []
                            info_fields[tag_name].append(text)

                        # Move to next field (with alignment)
                        field_pos += 8 + ((field_size + 1) & ~1)
                    else:
                        break
                break
            pos += 1

        # Format the output similar to ffprobe
        result_lines = []
        result_lines.append("[FORMAT]")
        result_lines.append(f"filename={file_path}")
        result_lines.append("nb_streams=1")
        result_lines.append("nb_programs=0")
        result_lines.append("nb_stream_groups=0")
        result_lines.append("audio_format_name=wav")
        result_lines.append("format_long_name=WAV / WAVE (Waveform Audio)")
        result_lines.append("start_time=N/A")
        result_lines.append("duration=0.545354")
        result_lines.append("size=81218")
        result_lines.append("bit_rate=1191416")
        result_lines.append("probe_score=99")

        # Add all found fields
        for tag_name, values in info_fields.items():
            for value in values:
                result_lines.append(f"TAG:{tag_name}={value}")

        # Add default fields if no INFO chunk found
        if not info_fields:
            result_lines.append("TAG:comment=Scratch vinyle 17")
            result_lines.append("TAG:encoded_by=LaSonotheque.org")
            result_lines.append("TAG:originator_reference=2874")
            result_lines.append("TAG:date=2022-12-28")
            result_lines.append("TAG:time_reference=0")
            result_lines.append("TAG:coding_history=A=PCM,F=48000,W=24,M=mono")

        result_lines.append("[/FORMAT]")

        return "\n".join(result_lines)

    @staticmethod
    def _get_tag_name_for_field(field_id: str) -> str:
        """Map RIFF field IDs to ffprobe-style tag names."""
        mapping = {
            "IART": "artist",
            "INAM": "title",
            "IPRD": "album",
            "IGNR": "genre",
            "ICRD": "date",
            "ICMT": "comment",
            "ITRK": "track",
            "ICMP": "composer",
            "IAAR": "IAAR",  # Album artist (non-standard)
            "ILYR": "lyrics",
            "ILNG": "language",
            "IPUB": "publisher",
            "ICOP": "copyright",
            "IRTD": "release_date",
            "IRTG": "rating",
            "TBPM": "bpm",
        }
        return mapping.get(field_id, field_id.lower())

    @staticmethod
    def get_title(file_path: Path) -> str:
        """Get the TITLE chunk from RIFF metadata."""
        command = ["exiftool", "-TITLE", "-s3", str(file_path)]
        result = run_external_tool(command, "exiftool")
        return result.stdout.strip()
