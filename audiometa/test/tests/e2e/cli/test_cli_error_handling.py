import subprocess
import sys
import pytest

from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


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
    
    def test_cli_yaml_format_without_pyyaml(self, sample_mp3_file, monkeypatch, capsys):
        # Test the format_output function directly with mocked yaml import
        from audiometa.cli import format_output
        import sys
        
        # Remove yaml from sys.modules if it exists
        if 'yaml' in sys.modules:
            del sys.modules['yaml']
        
        # Mock the import to raise ImportError
        original_import = __import__
        def mock_import(name, *args, **kwargs):
            if name == 'yaml':
                raise ImportError("No module named 'yaml'")
            return original_import(name, *args, **kwargs)
        
        monkeypatch.setattr('builtins.__import__', mock_import)
        
        # Test that format_output falls back to JSON when yaml is not available
        test_data = {"test": "data"}
        result = format_output(test_data, "yaml")
        
        # Should return JSON format
        import json
        expected_json = json.dumps(test_data, indent=2)
        assert result == expected_json
        
        # Should print warning to stderr
        captured = capsys.readouterr()
        assert "Warning: PyYAML not installed, falling back to JSON" in captured.err

    def test_cli_multiple_files_mixed_success_failure_continue_on_error(self, sample_mp3_file, sample_wav_file, tmp_path):
        # Create unsupported file type
        unsupported_file = tmp_path / "unsupported.txt"
        unsupported_file.write_text("not audio")
        
        # Run CLI with mixed files and continue_on_error=True
        result = subprocess.run([
            sys.executable, "-m", "audiometa", "read",
            str(sample_mp3_file), str(sample_wav_file), str(unsupported_file),
            "--continue-on-error"
        ], capture_output=True, text=True)
        
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
        result = subprocess.run([
            sys.executable, "-m", "audiometa", "read",
            str(sample_mp3_file), str(unsupported_file)
        ], capture_output=True, text=True)
        
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
        result = subprocess.run([
            sys.executable, "-m", "audiometa", "read",
            str(unsupported1), str(unsupported2),
            "--continue-on-error"
        ], capture_output=True, text=True)
        
        # Should succeed overall (exit code 0) despite all files failing
        assert result.returncode == 0
        
        # Should contain error messages for all failed files
        stderr_output = result.stderr.lower()
        assert "error" in stderr_output

    def test_cli_multiple_files_write_mixed_success_failure(self, tmp_path):
        with TempFileWithMetadata({}, "mp3") as temp_mp3, \
             TempFileWithMetadata({}, "flac") as temp_flac:
            
            # Create unsupported file type
            unsupported_file = tmp_path / "unsupported.txt"
            unsupported_file.write_text("not audio")
            
            # Run CLI write command with mixed files
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_mp3.path), str(temp_flac.path), str(unsupported_file),
                "--title", "Test Title",
                "--continue-on-error"
            ], capture_output=True, text=True)
            
            # Should succeed overall (exit code 0)
            assert result.returncode == 0
            
            # Should contain success messages for valid files
            stdout_output = result.stdout.lower()
            assert "updated metadata for" in stdout_output
            
            # Should contain error message for unsupported file
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output

    def test_cli_multiple_files_delete_mixed_success_failure(self, tmp_path):
        with TempFileWithMetadata({}, "mp3") as temp_mp3, \
             TempFileWithMetadata({}, "wav") as temp_wav:
            
            # Create unsupported file type
            unsupported_file = tmp_path / "unsupported.txt"
            unsupported_file.write_text("not audio")
            
            # Run CLI delete command with mixed files
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "delete",
                str(temp_mp3.path), str(temp_wav.path), str(unsupported_file),
                "--continue-on-error"
            ], capture_output=True, text=True)
            
            # Should succeed overall (exit code 0)
            assert result.returncode == 0
            
            # Should contain messages for processed files
            stdout_output = result.stdout.lower()
            assert "deleted" in stdout_output or "found" in stdout_output
            
            # Should contain error message for unsupported file
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output
