import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import cast, TypeAlias, Union

from mutagen.flac import FLAC
from mutagen.flac import StreamInfo
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

from .exceptions import FileByteMismatchError, FileCorruptedError, FileTypeNotSupportedError
from .utils.MetadataFormat import MetadataFormat

# Type alias for files that can be handled (must be disk-based)
DiskBasedFile: TypeAlias = Union[str, Path, bytes, object]


class AudioFile:
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
        elif hasattr(file, 'path'):
            # Handle objects with a path attribute (like TempFileWithMetadata)
            self.file = file
            self.file_path = str(file.path)
        elif hasattr(file, 'name'):
            # Handle file-like objects with a name attribute
            self.file = file
            self.file_path = file.name
        elif hasattr(file, 'temporary_file_path'):
            # Handle temporary uploaded files
            self.file = file
            self.file_path = file.temporary_file_path()
        else:
            raise FileTypeNotSupportedError(f"Unsupported file type: {type(file)}")

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File {self.file_path} does not exist")

        file_extension = os.path.splitext(self.file_path)[1].lower()
        self.file_extension = file_extension
        
        # Validate that the file type is supported
        supported_extensions = MetadataFormat.get_priorities().keys()
        if file_extension not in supported_extensions:
            raise FileTypeNotSupportedError(f"File type {file_extension} is not supported. Supported types: {', '.join(supported_extensions)}")

    def get_duration_in_sec(self) -> float:
        path = self.file_path

        if self.file_extension == '.mp3':
            try:
                audio = MP3(path)
                return audio.info.length
            except Exception as exc:
                # If MP3 fails, try other formats as fallback
                try:
                    return WAVE(path).info.length
                except:
                    try:
                        return FLAC(path).info.length
                    except:
                        raise exc  # If all attempts fail, raise original MP3 error

        elif self.file_extension == '.wav':
            try:
                # Use ffprobe to get duration, more tolerant of file format issues
                result = subprocess.run([
                    'ffprobe',
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_format',
                    '-show_streams',
                    path
                ], capture_output=True, text=True)

                if result.returncode != 0:
                    raise RuntimeError("Failed to probe audio file")

                data = json.loads(result.stdout)
                # Try format duration first, then stream duration if available
                duration = float(data.get('format', {}).get('duration') or
                                 next((s.get('duration') for s in data.get('streams', [])
                                       if s.get('duration')), 0))

                if duration <= 0:
                    raise RuntimeError("Could not determine audio duration")
                return duration

            except json.JSONDecodeError:
                raise RuntimeError("Failed to parse audio file metadata")
            except Exception as exc:
                if str(exc) == "Failed to probe audio file":
                    raise FileCorruptedError("ffprobe could not parse the audio file.")
                raise RuntimeError(f"Failed to read WAV file duration: {str(exc)}")

        elif self.file_extension == '.flac':
            try:
                return FLAC(path).info.length
            except Exception as exc:
                error_str = str(exc)
                if "file said" in error_str and "bytes, read" in error_str:
                    raise FileByteMismatchError(error_str.capitalize())
                raise
        else:
            raise FileTypeNotSupportedError(f"Reading is not supported for file type: {self.file_extension}")

    def get_bitrate(self) -> int:
        path = self.file_path
        if self.file_extension == '.mp3':
            audio = MP3(path)
            # Get MP3 bitrate directly from audio stream
            if audio.info.bitrate:
                return audio.info.bitrate // 1000  # Convert from bps to kbps
            return 0
        elif self.file_extension == '.wav':
            try:
                # Use ffprobe to get audio stream information
                result = subprocess.run([
                    'ffprobe',
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_streams',
                    '-select_streams', 'a:0',  # Select first audio stream
                    path
                ], capture_output=True, text=True)

                if result.returncode != 0:
                    raise RuntimeError("Failed to probe audio file")

                data = json.loads(result.stdout)
                if not data.get('streams'):
                    raise RuntimeError("No audio streams found")

                stream = data['streams'][0]
                # Get bitrate directly if available
                if 'bit_rate' in stream:
                    return int(stream['bit_rate']) // 1000

                # Calculate from sample_rate * channels * bits_per_sample if no direct bitrate
                sample_rate = int(stream.get('sample_rate', 0))
                channels = int(stream.get('channels', 0))
                bits_per_sample = int(stream.get('bits_per_raw_sample', 0) or stream.get('bits_per_sample', 0))

                if not all([sample_rate, channels, bits_per_sample]):
                    raise RuntimeError("Missing audio stream information")

                return (sample_rate * channels * bits_per_sample) // 1000
            except json.JSONDecodeError:
                raise RuntimeError("Failed to parse audio file metadata")
            except Exception as exc:
                raise RuntimeError(f"Failed to read WAV file bitrate: {str(exc)}")
        elif self.file_extension == '.flac':
            audio_info = cast(StreamInfo, FLAC(path).info)
            return int(audio_info.bitrate / 1000)
        else:
            raise FileTypeNotSupportedError(f"Reading is not supported for file type: {self.file_extension}")

    def read(self, size: int = -1) -> bytes:
        with open(self.file_path, 'rb') as f:
            return f.read(size)

    def write(self, data: bytes) -> int:
        with open(self.file_path, 'wb') as f:
            return f.write(data)

    def seek(self, offset: int, whence: int = 0) -> int:
        with open(self.file_path, 'rb') as f:
            return f.seek(offset, whence)

    def close(self) -> None:
        if hasattr(self.file, 'close'):
            self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_file_path_or_object(self) -> str:
        """Returns the path to the file on the filesystem."""
        return self.file_path

    def get_file_name_original(self) -> str:
        """
        "Original" means the name of the file that was uploaded by the user.
        The actual file name may be different if the file was renamed during the upload process.
        """
        if hasattr(self.file, 'name'):
            return self.file.name
        elif hasattr(self.file, 'path'):
            # Handle objects with a path attribute (like TempFileWithMetadata)
            return self.file.path.name
        elif isinstance(self.file, str):
            return os.path.basename(self.file)
        elif isinstance(self.file, Path):
            return self.file.name
        else:
            raise FileTypeNotSupportedError(f"Reading is not supported for file type: {type(self.file)}")

    def get_file_name_system(self) -> str:
        """
        Returns the actual filename in the system, which may be different from the original name
        if the file was renamed during upload or processing.
        """
        path = self.file_path
        return os.path.basename(path)

    def is_flac_file_md5_valid(self) -> bool:
        if not self.file_extension == '.flac':
            raise FileTypeNotSupportedError("The file is not a FLAC file")

        result = subprocess.run(['flac', '-t', self.file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output = result.stderr.decode()
        if 'ok' in output:
            return True
        if 'MD5 signature mismatch' in output:
            return False
        if 'FLAC__STREAM_DECODER_ERROR_STATUS_LOST_SYNC' in output:
            return False
        else:
            raise FileCorruptedError("The Flac file md5 check failed")

    def get_file_with_corrected_md5(self, delete_original: bool = False) -> str:
        """
        Returns a new temporary file with corrected MD5 signature.
        Returns the path to the corrected file.

        Args:
            delete_original: If True, deletes the original file after creating the corrected version.
                           Defaults to False to maintain backward compatibility.

        Raises:
            FileCorruptedError: If the FLAC file is corrupted or cannot be corrected
            RuntimeError: If the FLAC command fails to execute
            OSError: If deletion of the original file fails when delete_original is True
        """
        if not self.file_extension == '.flac':
            raise FileTypeNotSupportedError("The file is not a FLAC file")

        # Create a temporary file to store the corrected FLAC content
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.flac')
        temp_path = temp_file.name
        temp_file.close()  # Close but don't delete yet

        success = False
        try:
            # Read the input file and run FLAC command
            with open(self.file_path, 'rb') as f:
                result = subprocess.run(['flac', '-f', '--best', '-o', temp_path, '-'],
                                        stdin=f,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

            if result.returncode != 0:
                stderr = result.stderr.decode()
                if 'wrote' not in stderr:
                    # Try reencoding with ffmpeg as a fallback
                    ffmpeg_cmd = ['ffmpeg', '-i', self.file_path, '-c:a', 'flac', temp_path]

                    ffmpeg_result = subprocess.run(
                        ffmpeg_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    if ffmpeg_result.returncode != 0:
                        raise FileCorruptedError(
                            "The FLAC file MD5 check failed and reencoding attempts were unsuccessful. The file is probably corrupted."
                        )

            # Verify the output file exists and is valid
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                raise FileCorruptedError("Failed to create corrected FLAC file")

            success = True

            # If requested, try to delete the original file
            if delete_original and success:
                try:
                    os.unlink(self.file_path)
                except OSError as e:
                    raise OSError(f"Failed to delete original file: {str(e)}")

            return temp_path

        except (subprocess.SubprocessError, OSError) as e:
            raise RuntimeError(f"Failed to execute FLAC command: {str(e)}")
        except Exception as e:
            raise e
        finally:
            # Clean up the temp file only if we failed
            if not success and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass  # Ignore cleanup errors

    def get_sample_rate(self) -> int:
        """
        Get the sample rate of an audio file.
        
        Returns:
            Sample rate in Hz
            
        Raises:
            FileTypeNotSupportedError: If the file format is not supported
            FileNotFoundError: If the file does not exist
        """
        if self.file_extension == '.mp3':
            try:
                audio = MP3(self.file_path)
                return int(audio.info.sample_rate)
            except Exception:
                return 0
        elif self.file_extension == '.wav':
            try:
                result = subprocess.run([
                    'ffprobe',
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_streams',
                    '-select_streams', 'a:0',
                    self.file_path
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    return 0
                
                data = json.loads(result.stdout)
                if not data.get('streams'):
                    return 0
                
                stream = data['streams'][0]
                return int(stream.get('sample_rate', 0))
            except Exception:
                return 0
        elif self.file_extension == '.flac':
            try:
                audio_info = cast(StreamInfo, FLAC(self.file_path).info)
                return int(audio_info.sample_rate)
            except Exception:
                return 0
        else:
            raise FileTypeNotSupportedError(f"Reading is not supported for file type: {self.file_extension}")

    def get_channels(self) -> int:
        """
        Get the number of channels in an audio file.
        
        Returns:
            Number of channels
            
        Raises:
            FileTypeNotSupportedError: If the file format is not supported
            FileNotFoundError: If the file does not exist
        """
        if self.file_extension == '.mp3':
            try:
                audio = MP3(self.file_path)
                return int(audio.info.channels)
            except Exception:
                return 0
        elif self.file_extension == '.wav':
            try:
                result = subprocess.run([
                    'ffprobe',
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_streams',
                    '-select_streams', 'a:0',
                    self.file_path
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    return 0
                
                data = json.loads(result.stdout)
                if not data.get('streams'):
                    return 0
                
                stream = data['streams'][0]
                return int(stream.get('channels', 0))
            except Exception:
                return 0
        elif self.file_extension == '.flac':
            try:
                audio_info = cast(StreamInfo, FLAC(self.file_path).info)
                return int(audio_info.channels)
            except Exception:
                return 0
        else:
            raise FileTypeNotSupportedError(f"Reading is not supported for file type: {self.file_extension}")

    def get_file_size(self) -> int:
        """
        Get the file size in bytes.
        
        Returns:
            File size in bytes
        """
        try:
            return os.path.getsize(self.file_path)
        except OSError:
            return 0

    def get_format_name(self) -> str:
        """
        Get the human-readable format name.
        
        Returns:
            Format name (e.g., 'MP3', 'FLAC', 'WAV')
        """
        format_names = {
            '.mp3': 'MP3',
            '.flac': 'FLAC',
            '.wav': 'WAV'
        }
        return format_names.get(self.file_extension, 'Unknown')
