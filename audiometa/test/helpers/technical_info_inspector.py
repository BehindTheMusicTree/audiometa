import subprocess
from pathlib import Path

from audiometa.utils.tool_path_resolver import get_tool_path


class TechnicalInfoInspector:
    """Helper class for inspecting technical audio file information using mediainfo."""

    @staticmethod
    def _run_mediainfo(file_path: str | Path, output_format: str = "JSON") -> dict:
        """Run mediainfo on a file and return parsed output."""
        cmd = ["mediainfo", f"--Output={output_format}", str(file_path)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if output_format == "JSON":
                import json

                return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            msg = f"Failed to run mediainfo on {file_path}: {e}"
            raise RuntimeError(msg) from e
        except json.JSONDecodeError as e:
            msg = f"Failed to parse mediainfo output: {e}"
            raise RuntimeError(msg) from e
        else:
            return {"text": result.stdout}

    @staticmethod
    def get_bitrate(file_path: str | Path) -> int | None:
        """Get the bitrate of an audio file in kb/s using mediainfo."""
        try:
            data = TechnicalInfoInspector._run_mediainfo(file_path, "JSON")
            tracks = data.get("media", {}).get("track", [])
            for track in tracks:
                if track.get("@type") == "Audio":
                    bitrate_str = track.get("BitRate")
                    if bitrate_str:
                        # Handle formats like "128 kb/s" or "128000"
                        if "kb/s" in str(bitrate_str):
                            return int(str(bitrate_str).split()[0])
                        if str(bitrate_str).isdigit():
                            return int(bitrate_str) // 1000
        except Exception:
            return None
        else:
            return None

    @staticmethod
    def get_duration(file_path: str | Path) -> float | None:
        """Get the duration of an audio file in seconds using ffprobe.

        ffprobe is used instead of mediainfo because mediainfo's MP3 duration depends on its version
        (gapless handling was added in 26.10), so the pinned Ubuntu and macOS versions disagree.
        """
        try:
            result = subprocess.run(
                [
                    get_tool_path("ffprobe"),
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return float(result.stdout.strip())
        except Exception:
            return None

    @staticmethod
    def get_sample_rate(file_path: str | Path) -> int | None:
        """Get the sample rate of an audio file in Hz using mediainfo."""
        try:
            data = TechnicalInfoInspector._run_mediainfo(file_path, "JSON")
            tracks = data.get("media", {}).get("track", [])
            for track in tracks:
                if track.get("@type") == "Audio":
                    sample_rate_str = track.get("SamplingRate")
                    if sample_rate_str:
                        # Handle formats like "44100 Hz"
                        if "Hz" in sample_rate_str:
                            return int(sample_rate_str.split()[0])
                        return int(sample_rate_str)
        except Exception:
            return None
        else:
            return None

    @staticmethod
    def get_channels(file_path: str | Path) -> int | None:
        """Get the number of channels of an audio file using mediainfo."""
        try:
            data = TechnicalInfoInspector._run_mediainfo(file_path, "JSON")
            tracks = data.get("media", {}).get("track", [])
            for track in tracks:
                if track.get("@type") == "Audio":
                    channels_str = track.get("Channels")
                    if channels_str:
                        return int(channels_str)
        except Exception:
            return None
        else:
            return None

    @staticmethod
    def get_file_size(file_path: str | Path) -> int | None:
        """Get the file size of an audio file in bytes using mediainfo."""
        try:
            data = TechnicalInfoInspector._run_mediainfo(file_path, "JSON")
            tracks = data.get("media", {}).get("track", [])
            for track in tracks:
                if track.get("@type") == "General":
                    file_size_str = track.get("FileSize")
                    if file_size_str:
                        return int(file_size_str)
        except Exception:
            return None
        else:
            return None
