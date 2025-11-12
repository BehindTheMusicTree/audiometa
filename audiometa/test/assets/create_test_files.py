#!/usr/bin/env python3
"""Script to create test audio files for testing."""

import subprocess
from pathlib import Path


def create_silent_audio_file(output_path: Path, duration: float = 1.0, sample_rate: int = 44100):
    """Create a silent audio file using ffmpeg."""
    try:
        # Determine codec based on file extension
        ext = output_path.suffix.lower()
        if ext == ".mp3":
            codec = "libmp3lame"
            bitrate = "128k"
        elif ext == ".flac":
            codec = "flac"
            bitrate = None
        elif ext == ".wav":
            codec = "pcm_s16le"
            bitrate = None
        else:
            codec = "libmp3lame"
            bitrate = "128k"

        cmd = [
            "ffmpeg",
            "-f",
            "lavfi",
            "-i",
            f"anullsrc=duration={duration}:sample_rate={sample_rate}",
            "-c:a",
            codec,
            "-y",  # Overwrite output file
            str(output_path),
        ]

        if bitrate:
            cmd.insert(-1, "-b:a")
            cmd.insert(-1, bitrate)

        subprocess.run(cmd, check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    else:
        return True


def create_test_files():
    """Create test audio files in different formats."""
    test_dir = Path(__file__).parent
    test_dir.mkdir(exist_ok=True)

    # Create different format test files
    formats = [
        ("sample.mp3", 1.0),
        ("sample.flac", 1.0),
        ("sample.wav", 1.0),
    ]

    for filename, duration in formats:
        output_path = test_dir / filename
        if not output_path.exists():
            success = create_silent_audio_file(output_path, duration)
            if not success:
                pass
        else:
            pass


if __name__ == "__main__":
    create_test_files()
