import subprocess
import sys

import pytest


@pytest.mark.e2e
class TestCLIHelp:
    def test_cli_help(self):
        result = subprocess.run([sys.executable, "-m", "audiometa"], capture_output=True, text=True, check=False)
        assert result.returncode == 1  # Should exit with error
        assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_cli_read_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", "--help"], capture_output=True, text=True, check=False
        )
        assert result.returncode == 0
        assert "read" in result.stdout.lower()

    def test_cli_unified_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "unified", "--help"], capture_output=True, text=True, check=False
        )
        assert result.returncode == 0
        assert "unified" in result.stdout.lower()

    def test_cli_write_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "write", "--help"], capture_output=True, text=True, check=False
        )
        assert result.returncode == 0
        assert "write" in result.stdout.lower()

    def test_cli_delete_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "delete", "--help"], capture_output=True, text=True, check=False
        )
        assert result.returncode == 0
        assert "delete" in result.stdout.lower()
