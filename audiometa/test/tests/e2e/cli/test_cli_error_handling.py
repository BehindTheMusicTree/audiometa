import subprocess
import sys
import pytest


@pytest.mark.e2e
class TestCLIErrorHandling:
    
    def test_cli_read_nonexistent_file(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.mp3"
        result = subprocess.run([sys.executable, "-m", "audiometa", "read", str(nonexistent_file)], 
                              capture_output=True, text=True)
        assert result.returncode == 1
        assert "error" in result.stderr.lower()
    
    def test_cli_read_with_continue_on_error(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.mp3"
        result = subprocess.run([sys.executable, "-m", "audiometa", "read", 
                               str(nonexistent_file), "--continue-on-error"], 
                              capture_output=True, text=True)
        assert result.returncode == 0
    
    def test_cli_write_no_metadata(self, sample_mp3_file):
        result = subprocess.run([sys.executable, "-m", "audiometa", "write", str(sample_mp3_file)], 
                              capture_output=True, text=True)
        assert result.returncode == 1
        assert "no metadata fields specified" in result.stderr.lower()
