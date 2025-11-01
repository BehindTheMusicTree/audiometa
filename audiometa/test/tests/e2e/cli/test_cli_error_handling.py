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
