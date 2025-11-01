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

    def test_cli_output_file_permission_error(self, sample_mp3_file, tmp_path):
        # Create read-only directory
        read_only_dir = tmp_path / "readonly"
        read_only_dir.mkdir(mode=0o444)
        output_file = read_only_dir / "output.json"

        # Try to write output to a file in read-only directory
        result = subprocess.run([
            sys.executable, "-m", "audiometa", "read",
            str(sample_mp3_file), "--output", str(output_file)
        ], capture_output=True, text=True)
        
        # Should fail due to permission error
        assert result.returncode != 0
        # Should contain error message about permission or writing
        stderr_output = result.stderr.lower()
        assert "error" in stderr_output or "permission" in stderr_output or "cannot" in stderr_output

    def test_cli_output_file_permission_error_with_continue(self, sample_mp3_file, tmp_path):
        # Create read-only directory
        read_only_dir = tmp_path / "readonly"
        read_only_dir.mkdir(mode=0o444)
        output_file = read_only_dir / "output.json"

        # Try to write output with continue-on-error flag
        result = subprocess.run([
            sys.executable, "-m", "audiometa", "read",
            str(sample_mp3_file), "--output", str(output_file), "--continue-on-error"
        ], capture_output=True, text=True)
        
        # Should succeed overall (exit code 0) because continue-on-error prevents exit
        assert result.returncode == 0
        stderr_output = result.stderr.lower()
        assert "error" in stderr_output or "permission" in stderr_output or "denied" in stderr_output

    def test_cli_output_file_nonexistent_directory(self, sample_mp3_file, tmp_path):
        # Try to write to a file in a nonexistent directory
        nonexistent_dir = tmp_path / "nonexistent" / "subdir"
        output_file = nonexistent_dir / "output.json"

        result = subprocess.run([
            sys.executable, "-m", "audiometa", "read",
            str(sample_mp3_file), "--output", str(output_file)
        ], capture_output=True, text=True)
        
        # Should fail due to nonexistent directory
        assert result.returncode != 0
        stderr_output = result.stderr.lower()
        assert "error" in stderr_output

    def test_cli_output_file_unified_command(self, tmp_path):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            # Create read-only directory
            read_only_dir = tmp_path / "readonly"
            read_only_dir.mkdir(mode=0o444)
            output_file = read_only_dir / "output.json"

            result = subprocess.run([
                sys.executable, "-m", "audiometa", "unified",
                str(temp_file.path), "--output", str(output_file)
            ], capture_output=True, text=True)
            
            # Should fail due to permission error
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output or "permission" in stderr_output or "cannot" in stderr_output

    def test_cli_invalid_format_argument(self):
        result = subprocess.run([
            sys.executable, "-m", "audiometa", "read", "nonexistent.mp3", "--format", "invalid"
        ], capture_output=True, text=True)
        
        # Should fail due to invalid format choice
        assert result.returncode != 0
        # argparse should show error about invalid choice
        stderr_output = result.stderr.lower()
        assert "invalid choice" in stderr_output or "error" in stderr_output

    def test_cli_invalid_rating_value_negative(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--rating", "-5"
            ], capture_output=True, text=True)
            
            # Should fail due to negative rating
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output

    def test_cli_invalid_rating_value_too_high(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--rating", "150"
            ], capture_output=True, text=True)
            
            # Should fail due to rating > 100
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output

    def test_cli_invalid_rating_value_non_numeric(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--rating", "not-a-number"
            ], capture_output=True, text=True)
            
            # Should fail due to non-numeric rating
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "invalid" in stderr_output.lower() or "error" in stderr_output

    def test_cli_invalid_year_value_non_numeric(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--year", "not-a-year"
            ], capture_output=True, text=True)
            
            # Should fail due to non-numeric year
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "invalid" in stderr_output.lower() or "error" in stderr_output

    def test_cli_invalid_year_value_negative(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--year", "-2023"
            ], capture_output=True, text=True)
            
            # Should fail due to negative year
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output

    def test_cli_invalid_year_value_future(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            future_year = str(2030 + 1)  # One year beyond current year
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--year", future_year
            ], capture_output=True, text=True)
            
            # Should fail due to future year
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "error" in stderr_output

    def test_cli_write_no_metadata_fields(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path)
            ], capture_output=True, text=True)
            
            # Should fail due to no metadata fields
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "no metadata fields specified" in stderr_output

    def test_cli_conflicting_format_options_read(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "read",
                str(temp_file.path), "--format", "table", "--no-headers", "--no-technical"
            ], capture_output=True, text=True)
            
            # Should succeed - these options are compatible
            assert result.returncode == 0
            # Table format with no headers/technical should still work
            assert len(result.stdout.strip()) > 0

    def test_cli_invalid_output_path_empty_string(self):
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "read",
                str(temp_file.path), "--output", ""
            ], capture_output=True, text=True)
            
            # Should succeed - empty output path means stdout
            assert result.returncode == 0
            assert len(result.stdout.strip()) > 0

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

    def test_cli_write_empty_title_artist_album(self):
        """Test CLI write with empty string values for metadata (should fail - no valid metadata)."""
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--title", "", "--artist", "", "--album", ""
            ], capture_output=True, text=True)
            
            # Should fail - empty strings are not considered valid metadata
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "no metadata fields specified" in stderr_output

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

    def test_cli_unified_with_no_headers_technical_flags(self):
        """Test CLI unified command with --no-headers and --no-technical (should fail - invalid args)."""
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "unified",
                str(temp_file.path), "--no-headers", "--no-technical"
            ], capture_output=True, text=True)
            
            # Should fail - unified command doesn't accept these flags
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "unrecognized arguments" in stderr_output

    def test_cli_write_empty_title_artist_album(self):
        """Test CLI write with empty string values for metadata (should fail - no valid metadata)."""
        with TempFileWithMetadata({}, "mp3") as temp_file:
            result = subprocess.run([
                sys.executable, "-m", "audiometa", "write",
                str(temp_file.path), "--title", "", "--artist", "", "--album", ""
            ], capture_output=True, text=True)
            
            # Should fail - empty strings are not considered valid metadata
            assert result.returncode != 0
            stderr_output = result.stderr.lower()
            assert "no metadata fields specified" in stderr_output

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
