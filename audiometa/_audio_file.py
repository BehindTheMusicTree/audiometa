"""Audio file handling module."""

import contextlib
import json
import subprocess
import tempfile
import types
from pathlib import Path
from typing import cast

from mutagen.flac import FLAC, StreamInfo
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

from .exceptions import (
    AudioFileMetadataParseError,
    DurationNotFoundError,
    FileByteMismatchError,
    FileCorruptedError,
    FileTypeNotSupportedError,
    FlacMd5CheckFailedError,
    InvalidChunkDecodeError,
)
from .manager._rating_supporting.id3v2._id3v2_constants import ID3V2_HEADER_SIZE
from .manager._rating_supporting.riff._riff_constants import RIFF_HEADER_SIZE
from .utils.metadata_format import MetadataFormat
from .utils.mutagen_exception_handler import handle_mutagen_exception
from .utils.tool_path_resolver import get_tool_path

# Type alias for files that can be handled (must be disk-based)
type DiskBasedFile = str | Path | bytes | object


class _AudioFile:
    file: DiskBasedFile
    file_path: str

    def __init__(self, file: DiskBasedFile):
        if isinstance(file, str):
            self.file = file
            self.file_path = file
        elif isinstance(file, Path):
            # Handle pathlib.Path objects
            self.file = file
            self.file_path = str(file)
        elif hasattr(file, "path"):
            # Handle objects with a path attribute (like TempFileWithMetadata)
            self.file = file
            self.file_path = str(file.path)
        elif hasattr(file, "name"):
            # Handle file-like objects with a name attribute
            self.file = file
            self.file_path = file.name
        elif hasattr(file, "temporary_file_path"):
            # Handle temporary uploaded files
            self.file = file
            self.file_path = file.temporary_file_path()
        else:
            msg = f"Unsupported file type: {type(file)}"
            raise FileTypeNotSupportedError(msg)

        if not Path(self.file_path).exists():
            msg = f"File {self.file_path} does not exist"
            raise FileNotFoundError(msg)

        file_extension = Path(self.file_path).suffix.lower()
        self.file_extension = file_extension

        # Validate that the file type is supported
        supported_extensions = MetadataFormat.get_priorities().keys()
        if file_extension not in supported_extensions:
            msg = f"File type {file_extension} is not supported. Supported types: {', '.join(supported_extensions)}"
            raise FileTypeNotSupportedError(msg)

        # Validate that the file content is valid for the format
        try:
            if file_extension == ".mp3":
                MP3(self.file_path)
            elif file_extension == ".flac":
                FLAC(self.file_path)
            elif file_extension == ".wav":
                # Use custom WAV validation that handles ID3v2 tags
                self._validate_wav_file(self.file_path)
        except Exception as e:
            msg = f"The file content is corrupted or not a valid {file_extension.upper()} file: {e!s}"
            raise FileCorruptedError(msg) from e

    def get_duration_in_sec(self) -> float:
        path = self.file_path

        if self.file_extension == ".mp3":
            try:
                audio = MP3(path)
                return float(audio.info.length)
            except Exception as exc:
                # If MP3 fails, try other formats as fallback
                try:
                    wave_audio = WAVE(path)
                    return float(wave_audio.info.length)  # type: ignore[attr-defined,unused-ignore]
                except Exception:
                    try:
                        flac_audio = FLAC(path)
                        return float(flac_audio.info.length)  # type: ignore[attr-defined,unused-ignore]
                    except Exception:
                        msg = f"Could not determine duration for {path}"
                        raise DurationNotFoundError(msg) from exc

        elif self.file_extension == ".wav":
            try:
                # Use ffprobe to get duration, more tolerant of file format issues
                result = subprocess.run(
                    [
                        get_tool_path("ffprobe"),
                        "-v",
                        "quiet",
                        "-print_format",
                        "json",
                        "-show_format",
                        "-show_streams",
                        path,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode != 0:
                    msg = "Failed to probe audio file"
                    raise RuntimeError(msg)

                data = json.loads(result.stdout)
                # Try format duration first, then stream duration if available
                duration = float(
                    data.get("format", {}).get("duration")
                    or next((s.get("duration") for s in data.get("streams", []) if s.get("duration")), 0)
                )

                if duration <= 0:
                    msg = "Could not determine audio duration"
                    raise DurationNotFoundError(msg) from None
            except json.JSONDecodeError as e:
                msg = "Failed to parse audio file metadata from ffprobe output"
                raise AudioFileMetadataParseError(msg) from e
            except DurationNotFoundError:
                raise
            except Exception as exc:
                if str(exc) == "Failed to probe audio file":
                    msg = "ffprobe could not parse the audio file."
                    raise FileCorruptedError(msg) from exc
                msg = f"Failed to read WAV file duration: {exc!s}"
                raise RuntimeError(msg) from exc
            else:
                return duration

        elif self.file_extension == ".flac":
            try:
                return float(FLAC(path).info.length)
            except Exception as exc:
                error_str = str(exc)
                if "file said" in error_str and "bytes, read" in error_str:
                    raise FileByteMismatchError(error_str.capitalize()) from exc
                if "FLAC" in error_str or "chunk" in error_str.lower():
                    msg = f"Failed to decode FLAC chunks: {error_str}"
                    raise InvalidChunkDecodeError(msg) from exc
                handle_mutagen_exception("read duration from FLAC file", path, exc)
                return 0.0  # Never reached, but satisfies type checker
        else:
            msg = f"Reading is not supported for file type: {self.file_extension}"
            raise FileTypeNotSupportedError(msg)

    def get_bitrate(self) -> int:
        path = self.file_path
        if self.file_extension == ".mp3":
            audio = MP3(path)
            # Get MP3 bitrate directly from audio stream
            if audio.info.bitrate:
                return int(audio.info.bitrate) // 1000
            return 0
        if self.file_extension == ".wav":
            try:
                # Use ffprobe to get audio stream information
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v",
                        "quiet",
                        "-print_format",
                        "json",
                        "-show_streams",
                        "-select_streams",
                        "a:0",  # Select first audio stream
                        path,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode != 0:
                    msg = "Failed to probe audio file"
                    raise RuntimeError(msg) from None

                data = json.loads(result.stdout)
                if not data.get("streams"):
                    msg = "No audio streams found"
                    raise RuntimeError(msg) from None

                stream = data["streams"][0]
                # Get bitrate directly if available
                if "bit_rate" in stream:
                    return int(stream["bit_rate"]) // 1000

                # Calculate from sample_rate * channels * bits_per_sample if no direct bitrate
                sample_rate = int(stream.get("sample_rate", 0))
                channels = int(stream.get("channels", 0))
                bits_per_sample = int(stream.get("bits_per_raw_sample", 0) or stream.get("bits_per_sample", 0))

                if not all([sample_rate, channels, bits_per_sample]):
                    msg = "Missing audio stream information"
                    raise RuntimeError(msg) from None

                return (sample_rate * channels * bits_per_sample) // 1000
            except json.JSONDecodeError as e:
                msg = "Failed to parse audio file metadata from ffprobe output"
                raise AudioFileMetadataParseError(msg) from e
            except Exception as exc:
                msg = f"Failed to read WAV file bitrate: {exc!s}"
                raise RuntimeError(msg) from exc
        elif self.file_extension == ".flac":
            audio_info = cast(StreamInfo, FLAC(path).info)
            return int(float(audio_info.bitrate) / 1000)
        else:
            msg = f"Reading is not supported for file type: {self.file_extension}"
            raise FileTypeNotSupportedError(msg)

    def read(self, size: int = -1) -> bytes:
        with Path(self.file_path).open("rb") as f:
            return f.read(size)

    def write(self, data: bytes) -> int:
        with Path(self.file_path).open("wb") as f:
            return f.write(data)

    def seek(self, offset: int, whence: int = 0) -> int:
        with Path(self.file_path).open("rb") as f:
            return f.seek(offset, whence)

    def close(self) -> None:
        if hasattr(self.file, "close"):
            self.file.close()

    def __enter__(self) -> "_AudioFile":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        self.close()

    def get_file_path_or_object(self) -> str:
        """Get the path to the file on the filesystem."""
        return self.file_path

    def _is_md5_unset(self) -> bool:
        """Check if FLAC file has unset MD5 checksum (all zeros)."""
        try:
            with Path(self.file_path).open("rb") as f:
                data = f.read()
                flac_marker_pos = data.find(b"fLaC")
                if flac_marker_pos == -1:
                    return False
                md5_start = flac_marker_pos + 4 + 1 + 18
                if md5_start + 16 > len(data):
                    return False
                md5_bytes = data[md5_start : md5_start + 16]
                return md5_bytes == b"\x00" * 16
        except Exception:
            return False

    def is_flac_file_md5_valid(self) -> bool:
        if self.file_extension != ".flac":
            msg = "The file is not a FLAC file"
            raise FileTypeNotSupportedError(msg)

        if self._is_md5_unset():
            return False

        result = subprocess.run([get_tool_path("flac"), "-t", self.file_path], capture_output=True, check=False)

        # Combine stdout and stderr as flac may output to either
        stdout_output = result.stdout.decode()
        stderr_output = result.stderr.decode()
        combined_output = stdout_output + stderr_output

        # flac -t returns 0 on success, non-zero on error
        # If return code is non-zero, the file is invalid
        if result.returncode != 0:
            return False

        # Check for explicit error messages (shouldn't happen with return code 0, but defensive)
        if "MD5 signature mismatch" in combined_output:
            return False
        if "FLAC__STREAM_DECODER_ERROR_STATUS_LOST_SYNC" in combined_output:
            return False

        # Check for explicit success message
        if "ok" in combined_output.lower():
            return True

        # If return code was 0 but no "ok" found, something unexpected happened
        msg = "The Flac file md5 check failed"
        raise FlacMd5CheckFailedError(msg)

    def get_file_with_corrected_md5(self, delete_original: bool = False) -> str:
        """Get a new temporary file with corrected MD5 signature. Returns the path to the corrected file.

        Args:
            delete_original: If True, deletes the original file after creating the corrected version.
                           Defaults to False to maintain backward compatibility.

        Raises:
            FileCorruptedError: If the FLAC file is corrupted or cannot be corrected
            RuntimeError: If the FLAC command fails to execute
            OSError: If deletion of the original file fails when delete_original is True
        """
        if self.file_extension != ".flac":
            msg = "The file is not a FLAC file"
            raise FileTypeNotSupportedError(msg)

        # Create a temporary file to store the corrected FLAC content
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".flac")
        temp_path = temp_file.name
        temp_file.close()  # Close but don't delete yet

        success = False
        try:
            # Read the input file and run FLAC command
            with Path(self.file_path).open("rb") as f:
                result = subprocess.run(
                    [get_tool_path("flac"), "-f", "--best", "-o", temp_path, "-"],
                    stdin=f,
                    capture_output=True,
                    check=False,
                )

            if result.returncode != 0:
                stderr = result.stderr.decode()
                if "wrote" not in stderr:
                    # Clean up any empty file created by failed flac command
                    temp_path_obj = Path(temp_path)
                    if temp_path_obj.exists() and temp_path_obj.stat().st_size == 0:
                        temp_path_obj.unlink(missing_ok=True)

                    # Try reencoding with ffmpeg as a fallback
                    # Use -y to overwrite any existing file
                    ffmpeg_cmd = [get_tool_path("ffmpeg"), "-i", self.file_path, "-c:a", "flac", "-y", temp_path]

                    ffmpeg_result = subprocess.run(ffmpeg_cmd, capture_output=True, check=False)

                    if ffmpeg_result.returncode != 0:
                        msg = (
                            "The FLAC file MD5 check failed and reencoding attempts were unsuccessful. "
                            "The file is probably corrupted."
                        )
                        raise FileCorruptedError(msg)

            # Verify the output file exists and is valid
            temp_path_obj = Path(temp_path)
            if not temp_path_obj.exists() or temp_path_obj.stat().st_size == 0:
                msg = "Failed to create corrected FLAC file"
                raise FileCorruptedError(msg)

            success = True

            # If requested, try to delete the original file
            if delete_original and success:
                try:
                    Path(self.file_path).unlink()
                except OSError as e:
                    msg = f"Failed to delete original file: {e!s}"
                    raise OSError(msg) from e

        except (subprocess.SubprocessError, OSError) as e:
            msg = f"Failed to execute FLAC command: {e!s}"
            raise RuntimeError(msg) from e
        except Exception as e:
            handle_mutagen_exception("fix FLAC MD5 checksum", self.file_path, e)
            return ""  # Never reached, but satisfies type checker
        else:
            return temp_path
        finally:
            # Clean up the temp file only if we failed
            if not success and Path(temp_path).exists():
                with contextlib.suppress(OSError):
                    Path(temp_path).unlink()

    def get_sample_rate(self) -> int:
        """Get the sample rate of an audio file.

        Returns:
            Sample rate in Hz

        Raises:
            FileTypeNotSupportedError: If the file format is not supported
            FileNotFoundError: If the file does not exist
        """
        if self.file_extension == ".mp3":
            try:
                audio = MP3(self.file_path)
                if audio.info.sample_rate is not None:
                    return int(float(audio.info.sample_rate))
            except Exception:
                pass
            return 0
        if self.file_extension == ".wav":
            try:
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v",
                        "quiet",
                        "-print_format",
                        "json",
                        "-show_streams",
                        "-select_streams",
                        "a:0",
                        self.file_path,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode != 0:
                    return 0

                data = json.loads(result.stdout)
                if not data.get("streams"):
                    return 0

                stream = data["streams"][0]
                return int(stream.get("sample_rate", 0))
            except Exception:
                return 0
        elif self.file_extension == ".flac":
            try:
                audio_info = cast(StreamInfo, FLAC(self.file_path).info)
                return int(float(audio_info.sample_rate))
            except Exception:
                return 0
        else:
            msg = f"Reading is not supported for file type: {self.file_extension}"
            raise FileTypeNotSupportedError(msg)

    def get_channels(self) -> int:
        """Get the number of channels in an audio file.

        Returns:
            Number of channels

        Raises:
            FileTypeNotSupportedError: If the file format is not supported
            FileNotFoundError: If the file does not exist
        """
        if self.file_extension == ".mp3":
            try:
                audio = MP3(self.file_path)
                if audio.info.channels is not None:
                    return int(float(audio.info.channels))
            except Exception:
                pass
            return 0
        if self.file_extension == ".wav":
            try:
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v",
                        "quiet",
                        "-print_format",
                        "json",
                        "-show_streams",
                        "-select_streams",
                        "a:0",
                        self.file_path,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode != 0:
                    return 0

                data = json.loads(result.stdout)
                if not data.get("streams"):
                    return 0

                stream = data["streams"][0]
                return int(stream.get("channels", 0))
            except Exception:
                return 0
        elif self.file_extension == ".flac":
            try:
                audio_info = cast(StreamInfo, FLAC(self.file_path).info)
                return int(float(audio_info.channels))
            except Exception:
                return 0
        else:
            msg = f"Reading is not supported for file type: {self.file_extension}"
            raise FileTypeNotSupportedError(msg)

    def get_file_size(self) -> int:
        """Get the file size in bytes.

        Returns:
            File size in bytes
        """
        try:
            return Path(self.file_path).stat().st_size
        except OSError:
            return 0

    def get_audio_format_name(self) -> str:
        """Get the human-readable format name.

        Returns:
            Audio format name (e.g., 'MP3', 'FLAC', 'WAV')
        """
        audio_format_names = {".mp3": "MP3", ".flac": "FLAC", ".wav": "WAV"}
        return audio_format_names.get(self.file_extension, "Unknown")

    def _skip_id3v2_tags(self, data: bytes) -> bytes:
        """Skip ID3v2 tags if present at the start of the file.

        Returns the data starting from after any ID3v2 tags.
        """
        if data.startswith(b"ID3"):
            # ID3v2 header is 10 bytes:
            # 3 bytes: ID3
            # 2 bytes: version
            # 1 byte: flags
            # 4 bytes: size (synchsafe integer)
            if len(data) < ID3V2_HEADER_SIZE:
                return data

            # Get size from synchsafe integer (7 bits per byte)
            size_bytes = data[6:ID3V2_HEADER_SIZE]
            size = (
                ((size_bytes[0] & 0x7F) << 21)
                | ((size_bytes[1] & 0x7F) << 14)
                | ((size_bytes[2] & 0x7F) << 7)
                | (size_bytes[3] & 0x7F)
            )

            # Skip the header (10 bytes) plus the size of the tag
            return data[ID3V2_HEADER_SIZE + size :]
        return data

    def _validate_wav_file(self, file_path: str) -> None:
        """Validate WAV file structure, handling ID3v2 tags at the beginning.

        This method performs lightweight validation of the RIFF/WAV structure without relying on mutagen for files that
        have ID3v2 tags.
        """
        with Path(file_path).open("rb") as f:
            # Read enough data to cover potential ID3v2 tags (up to ~1MB for very large tags)
            header_data = f.read(RIFF_HEADER_SIZE)

            # Skip ID3v2 tags if present
            if header_data.startswith(b"ID3"):
                # Read the full file to properly handle ID3v2 tags
                f.seek(0)
                full_data = f.read()

                # Skip the ID3v2 tag
                clean_data = self._skip_id3v2_tags(full_data)

                # Check if we have enough data for RIFF header after skipping ID3v2
                if len(clean_data) < RIFF_HEADER_SIZE:
                    msg = "File too small after skipping ID3v2 tags"
                    raise FileCorruptedError(msg)

                riff_header = clean_data[:RIFF_HEADER_SIZE]
            else:
                riff_header = header_data

            # Validate RIFF header
            if len(riff_header) < RIFF_HEADER_SIZE:
                msg = "File too small to contain RIFF header"
                raise FileCorruptedError(msg)

            if not riff_header.startswith(b"RIFF"):
                msg = "Invalid RIFF header"
                raise FileCorruptedError(msg)

            if riff_header[8:12] != b"WAVE":
                msg = "Not a WAVE file"
                raise FileCorruptedError(msg)

            # Basic structure validation passed
            return
