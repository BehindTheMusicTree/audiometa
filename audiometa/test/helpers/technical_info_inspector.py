import subprocess
from pathlib import Path
from typing import Optional


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
            else:
                return {"text": result.stdout}
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to run mediainfo on {file_path}: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse mediainfo output: {e}")

    @staticmethod
    def get_bitrate(file_path: str | Path) -> Optional[int]:
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
                        elif str(bitrate_str).isdigit():
                            return int(bitrate_str) // 1000
            return None
        except Exception:
            return None

    @staticmethod
    def get_duration(file_path: str | Path) -> Optional[float]:
        """Get the duration of an audio file in seconds using mediainfo."""
        try:
            data = TechnicalInfoInspector._run_mediainfo(file_path, "JSON")
            tracks = data.get("media", {}).get("track", [])
            for track in tracks:
                if track.get("@type") == "General":
                    duration_str = track.get("Duration")
                    if duration_str:
                        # Handle formats like "1.025 s" or just numbers
                        if "s" in duration_str:
                            return float(duration_str.split()[0])
                        else:
                            return float(duration_str)
            return None
        except Exception:
            return None

    @staticmethod
    def get_sample_rate(file_path: str | Path) -> Optional[int]:
        """Get the sample rate of an audio file in Hz using mediainfo."""
        try:
            data = TechnicalInfoInspector._run_mediainfo(file_path, "JSON")
            tracks = data.get("media", {}).get("track", [])
            for track in tracks:
                if track.get("@type") == "Audio":
                    sample_rate_str = track.get("Sampling_rate")
                    if sample_rate_str:
                        # Handle formats like "44100 Hz"
                        if "Hz" in sample_rate_str:
                            return int(sample_rate_str.split()[0])
                        else:
                            return int(sample_rate_str)
            return None
        except Exception:
            return None