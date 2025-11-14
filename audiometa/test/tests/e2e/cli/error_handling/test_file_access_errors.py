import stat
import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIFileAccessErrors:
    def test_cli_read_nonexistent_file(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.mp3"
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(nonexistent_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 1
        assert "error" in result.stderr.lower()

    def test_cli_read_with_continue_on_error(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.mp3"
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(nonexistent_file), "--continue-on-error"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0

    def test_cli_output_file_permission_error(self, sample_mp3_file, tmp_path):
        # Create read-only file (more reliable cross-platform than read-only directory)
        output_file = tmp_path / "output.json"
        output_file.write_text("existing content")
        # Make file read-only
        output_file.chmod(stat.S_IREAD)

        try:
            # Try to write output to read-only file
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(sample_mp3_file), "--output", str(output_file)],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should fail due to permission error
            assert result.returncode != 0
            # Should contain error message about permission or writing
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output or "permission" in stderr_output or "cannot" in stderr_output
        finally:
            # Restore write permissions for cleanup
            output_file.chmod(stat.S_IWRITE | stat.S_IREAD)

    def test_cli_output_file_permission_error_with_continue(self, sample_mp3_file, tmp_path):
        # Create read-only file (more reliable cross-platform than read-only directory)
        output_file = tmp_path / "output.json"
        output_file.write_text("existing content")
        # Make file read-only
        output_file.chmod(stat.S_IREAD)

        try:
            # Try to write output with continue-on-error flag
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "read",
                    str(sample_mp3_file),
                    "--output",
                    str(output_file),
                    "--continue-on-error",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should succeed overall (exit code 0) because continue-on-error prevents exit
            assert result.returncode == 0
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output or "permission" in stderr_output or "denied" in stderr_output
        finally:
            # Restore write permissions for cleanup
            output_file.chmod(stat.S_IWRITE | stat.S_IREAD)

    def test_cli_output_file_nonexistent_directory(self, sample_mp3_file, tmp_path):
        # Try to write to a file in a nonexistent directory
        nonexistent_dir = tmp_path / "nonexistent" / "subdir"
        output_file = nonexistent_dir / "output.json"

        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(sample_mp3_file), "--output", str(output_file)],
            capture_output=True,
            text=True,
            check=False,
        )

        # Should fail due to nonexistent directory
        assert result.returncode != 0
        stderr_output = result.stderr.lower()
        assert "error" in stderr_output

    def test_cli_output_file_unified_command(self, tmp_path):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            # Create read-only file (more reliable cross-platform than read-only directory)
            output_file = tmp_path / "output.json"
            output_file.write_text("existing content")
            # Make file read-only
            output_file.chmod(stat.S_IREAD)

            try:
                result = subprocess.run(
                    [sys.executable, "-m", "audiometa", "unified", str(temp_file_path), "--output", str(output_file)],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                # Should fail due to permission error
                assert result.returncode != 0
                stderr_output = result.stderr.lower()
                assert "error" in stderr_output or "permission" in stderr_output or "cannot" in stderr_output
            finally:
                # Restore write permissions for cleanup
                output_file.chmod(stat.S_IWRITE | stat.S_IREAD)
