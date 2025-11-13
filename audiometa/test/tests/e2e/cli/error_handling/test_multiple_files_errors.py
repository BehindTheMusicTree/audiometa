import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIMultipleFilesErrors:
    def test_cli_multiple_files_mixed_success_failure_continue_on_error(
        self, sample_mp3_file, sample_wav_file, tmp_path
    ):
        # Create unsupported file type
        unsupported_file = tmp_path / "unsupported.txt"
        unsupported_file.write_text("not audio")

        # Run CLI with mixed files and continue_on_error=True
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "audiometa",
                "read",
                str(sample_mp3_file),
                str(sample_wav_file),
                str(unsupported_file),
                "--continue-on-error",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Should succeed overall (exit code 0)
        assert result.returncode == 0

        # Should contain error messages for failed files
        stderr_output = result.stderr.lower()
        assert "error processing" in stderr_output or "error" in stderr_output

        # Should contain output for successful files (at least some JSON output)
        assert "{" in result.stdout or "}" in result.stdout

    def test_cli_multiple_files_mixed_success_failure_no_continue(self, sample_mp3_file, tmp_path):
        # Create unsupported file type
        unsupported_file = tmp_path / "unsupported.txt"
        unsupported_file.write_text("not audio")

        # Run CLI with mixed files and continue_on_error=False (default)
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(sample_mp3_file), str(unsupported_file)],
            capture_output=True,
            text=True,
            check=False,
        )

        # Should fail overall (exit code 1) due to the unsupported file
        assert result.returncode == 1

        # Should contain error message
        stderr_output = result.stderr.lower()
        assert "error" in stderr_output

    def test_cli_multiple_files_all_fail_continue_on_error(self, tmp_path):
        # Create unsupported files
        unsupported1 = tmp_path / "unsupported1.txt"
        unsupported1.write_text("not audio")

        unsupported2 = tmp_path / "unsupported2.jpg"
        unsupported2.write_text("not audio")

        # Run CLI with all failing files and continue_on_error=True
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(unsupported1), str(unsupported2), "--continue-on-error"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Should succeed overall (exit code 0) despite all files failing
        assert result.returncode == 0

        # Should contain error messages for all failed files
        stderr_output = result.stderr.lower()
        assert "error" in stderr_output

    def test_cli_multiple_files_write_mixed_success_failure(self, tmp_path):
        with temp_file_with_metadata({}, "mp3") as temp_mp3_path, temp_file_with_metadata({}, "flac") as temp_flac_path:
            # Create unsupported file type
            unsupported_file = tmp_path / "unsupported.txt"
            unsupported_file.write_text("not audio")

            # Run CLI write command with mixed files
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "write",
                    str(temp_mp3_path),
                    str(temp_flac_path),
                    str(unsupported_file),
                    "--title",
                    "Test Title",
                    "--continue-on-error",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should succeed overall (exit code 0)
            assert result.returncode == 0

            # Should contain success messages for valid files
            stdout_output = result.stdout.lower()
            assert (
                "updated metadata for" in stdout_output
            ), f"Expected success message in stdout but got:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

            # Should contain error message for unsupported file
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output

    def test_cli_multiple_files_delete_mixed_success_failure(self, tmp_path):
        with temp_file_with_metadata({}, "mp3") as temp_mp3_path, temp_file_with_metadata({}, "wav") as temp_wav_path:
            # Create unsupported file type
            unsupported_file = tmp_path / "unsupported.txt"
            unsupported_file.write_text("not audio")

            # Run CLI delete command with mixed files
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "delete",
                    str(temp_mp3_path),
                    str(temp_wav_path),
                    str(unsupported_file),
                    "--continue-on-error",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should succeed overall (exit code 0)
            assert result.returncode == 0

            # Should contain messages for processed files
            stdout_output = result.stdout.lower()
            assert (
                "deleted" in stdout_output or "found" in stdout_output
            ), f"Expected success message in stdout but got:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

            # Should contain error message for unsupported file
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output
