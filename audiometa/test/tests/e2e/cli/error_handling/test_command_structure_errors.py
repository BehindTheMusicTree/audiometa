import subprocess
import sys
import pytest

from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.e2e
class TestCLICommandStructureErrors:

    def test_cli_unified_with_no_headers_technical_flags(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "unified",
                str(temp_file.path), "--no-headers", "--no-technical"
            ], capture_output=True, text=True)

            # Should fail - unified command doesn't accept these flags
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "unrecognized arguments" in stderr_output

    def test_cli_read_help_flag(self):
        result = subprocess.run([
            sys.executable, "-m", "audiometa", "read", "--help"
        ], capture_output=True, text=True)

        # Should show read command help
        assert result.returncode == 0
        stdout_output = result.stdout.lower()
        assert "read" in stdout_output and "files" in stdout_output

    def test_cli_recursive_with_single_file(self):
        """Test CLI recursive flag with single file (should work but be redundant)."""
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "read",
                str(temp_file.path), "--recursive"
            ], capture_output=True, text=True)

            # Should succeed - recursive with single file is valid
            assert result.returncode == 0
            assert len(result.stdout.strip()) > 0

    def test_cli_invalid_command(self):
        result = subprocess.run([
            sys.executable, "-m", "audiometa", "invalidcommand"
        ], capture_output=True, text=True)

        # Should fail due to invalid command
        assert result.returncode != 0
        stderr_output = result.stderr.lower()
        assert "invalid choice" in stderr_output or "error" in stderr_output

    def test_cli_no_command(self):
        result = subprocess.run([
            sys.executable, "-m", "audiometa"
        ], capture_output=True, text=True)

        # Should show help and exit with code 1
        assert result.returncode == 1
        stdout_output = result.stdout.lower()
        assert "usage" in stdout_output or "help" in stdout_output

    def test_cli_help_flag(self):
        result = subprocess.run([
            sys.executable, "-m", "audiometa", "--help"
        ], capture_output=True, text=True)

        # Should show help and exit successfully
        assert result.returncode == 0
        stdout_output = result.stdout.lower()
        assert "usage" in stdout_output and "help" in stdout_output