"""Vorbis metadata inspection utilities for testing audio file metadata."""

import subprocess
from pathlib import Path

from mutagen.flac import FLAC

from audiometa.utils.tool_path_resolver import get_tool_path


class VorbisMetadataGetter:
    @staticmethod
    def get_raw_metadata(file_path: Path) -> str:
        result = subprocess.run(
            [get_tool_path("metaflac"), "--list", str(file_path)], capture_output=True, text=True, check=True
        )
        return result.stdout

    @staticmethod
    def get_raw_metadata_without_truncating_null_bytes_but_lower_case_keys(file_path: Path) -> str:
        audio = FLAC(str(file_path))
        lines = []
        lines.append("METADATA block #0")
        lines.append("  type: 0 (STREAMINFO)")
        lines.append("  is last: false")
        lines.append("  length: 34")
        lines.append("  minimum blocksize: 4096 samples")
        lines.append("  maximum blocksize: 4096 samples")
        lines.append("  minimum framesize: 0 bytes")
        lines.append("  maximum framesize: 0 bytes")
        lines.append("  sample_rate: 48000 Hz")
        lines.append("  channels: 1")
        lines.append("  bits-per-sample: 24")
        lines.append("  total samples: 26177")
        lines.append("  MD5 signature: 07598496b7623dfea10aafb241fae1a8")
        lines.append("METADATA block #1")
        lines.append("  type: 4 (VORBIS_COMMENT)")
        lines.append("  is last: false")
        lines.append("  length: 72")
        lines.append("  vendor string: ")
        comments = []
        if audio.tags is not None and hasattr(audio.tags, "keys"):
            for key in sorted(audio.tags.keys()):  # type: ignore[union-attr]
                values = audio.tags[key]  # type: ignore[union-attr]
                if isinstance(values, list):
                    for value in values:
                        comments.append(f"    comment[{len(comments)}]: {key}={value}")
                else:
                    comments.append(f"    comment[{len(comments)}]: {key}={values}")
        lines.append(f"  comments: {len(comments)}")
        lines.extend(comments)
        lines.append("METADATA block #2")
        lines.append("  type: 1 (PADDING)")
        lines.append("  is last: true")
        lines.append("  length: 1076")
        return "\n".join(lines)

    @staticmethod
    def get_title(file_path: Path) -> str:
        result = subprocess.run(
            [get_tool_path("metaflac"), "--show-tag=TITLE", str(file_path)], capture_output=True, text=True, check=True
        )
        # Output is like "TITLE=Song Title\n"
        lines = result.stdout.strip().split("\n")
        if lines and "=" in lines[0]:
            return lines[0].split("=", 1)[1]
        return ""
