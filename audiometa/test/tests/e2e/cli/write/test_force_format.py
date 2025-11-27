import platform
import subprocess
import sys

import pytest

from audiometa import get_unified_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.e2e
class TestCLIWriteForceFormat:
    def test_cli_write_force_format_id3v2_mp3(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "CLI Force ID3v2 Title",
                    "--force-format",
                    "id3v2",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Updated metadata" in result.stdout

            metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "CLI Force ID3v2 Title"

    def test_cli_write_force_format_id3v1_mp3(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "CLI Force ID3v1 Title",
                    "--force-format",
                    "id3v1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Updated metadata" in result.stdout

            metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "CLI Force ID3v1 Title"

    def test_cli_write_force_format_vorbis_flac(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "CLI Force Vorbis Title",
                    "--force-format",
                    "vorbis",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Updated metadata" in result.stdout

            metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.VORBIS)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "CLI Force Vorbis Title"

    def test_cli_write_force_format_riff_wav(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "CLI Force RIFF Title",
                    "--force-format",
                    "riff",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Updated metadata" in result.stdout

            metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "CLI Force RIFF Title"

    def test_cli_write_force_format_unsupported_format_mp3(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "Test Title",
                    "--force-format",
                    "vorbis",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "not supported" in stderr_output or "error" in stderr_output

    def test_cli_write_force_format_writes_only_to_specified_format(self):
        with temp_file_with_metadata({"title": "Original RIFF Title"}, "wav") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "New ID3v2 Title",
                    "--force-format",
                    "id3v2",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            riff_metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.RIFF)
            id3v2_metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)

            assert riff_metadata.get(UnifiedMetadataKey.TITLE) == "Original RIFF Title"
            assert id3v2_metadata.get(UnifiedMetadataKey.TITLE) == "New ID3v2 Title"

    @pytest.mark.skipif(platform.system() == "Windows", reason="id3v2 tool requires WSL on Windows")
    def test_cli_write_force_format_id3v2_flac(self):
        """Test forcing ID3v2 format on FLAC files.

        Note: This test is skipped on Windows because writing ID3v2 tags to FLAC files
        requires the external 'id3v2' tool (mutagen corrupts FLAC structure). On Windows,
        the 'id3v2' tool is not available as a native binary and requires WSL (Windows
        Subsystem for Linux), which is not set up in Windows CI environments.
        """
        with temp_file_with_metadata({}, "flac") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "CLI Force ID3v2 FLAC Title",
                    "--force-format",
                    "id3v2",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Updated metadata" in result.stdout

            metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "CLI Force ID3v2 FLAC Title"

    def test_cli_write_force_format_id3v1_flac(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "CLI Force ID3v1 FLAC Title",
                    "--force-format",
                    "id3v1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Updated metadata" in result.stdout

            metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "CLI Force ID3v1 FLAC Title"

    def test_cli_write_force_format_id3v1_wav(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "CLI Force ID3v1 WAV Title",
                    "--force-format",
                    "id3v1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            assert "Updated metadata" in result.stdout

            metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "CLI Force ID3v1 WAV Title"

    def test_cli_write_force_format_with_multiple_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "Multi Field Title",
                    "--artist",
                    "Multi Field Artist",
                    "--album",
                    "Multi Field Album",
                    "--force-format",
                    "id3v2",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "Multi Field Title"
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["Multi Field Artist"]
            assert metadata.get(UnifiedMetadataKey.ALBUM) == "Multi Field Album"

    def test_cli_write_force_format_with_rating(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "Rating Test Title",
                    "--rating",
                    "85",
                    "--force-format",
                    "id3v2",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0

            metadata = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "Rating Test Title"
            assert metadata.get(UnifiedMetadataKey.RATING) is not None

    def test_cli_write_force_format_unsupported_flac_riff(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "Test Title",
                    "--force-format",
                    "riff",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "not supported" in stderr_output or "error" in stderr_output

    def test_cli_write_force_format_unsupported_wav_vorbis(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(test_file),
                    "--title",
                    "Test Title",
                    "--force-format",
                    "vorbis",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "not supported" in stderr_output or "error" in stderr_output
