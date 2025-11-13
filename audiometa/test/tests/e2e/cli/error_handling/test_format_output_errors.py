import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIFormatOutputErrors:
    def test_cli_yaml_format_with_pyyaml(self, capsys):
        # Test the format_output function when PyYAML is installed
        import json

        from audiometa.cli import format_output

        # Test that format_output uses YAML when yaml is available
        test_data = {"test": "data", "number": 42}
        result = format_output(test_data, "yaml")

        # Should NOT be JSON (YAML format is different)
        json_result = json.dumps(test_data, indent=2)
        assert result != json_result

        # Should NOT print warning to stderr
        captured = capsys.readouterr()
        assert "Warning: PyYAML not installed" not in captured.err
        assert "falling back" not in captured.err

        # Result should contain YAML formatting (includes colons for key-value pairs)
        assert "test: data" in result or "test: 'data'" in result
        assert "number: 42" in result

    def test_cli_yaml_format_without_pyyaml(self, monkeypatch, capsys):
        # Test the format_output function directly with mocked yaml import
        import sys

        from audiometa.cli import format_output

        # Remove yaml from sys.modules if it exists
        if "yaml" in sys.modules:
            del sys.modules["yaml"]

        # Mock the import to raise ImportError
        original_import = __import__

        def mock_import(name, *args, **kwargs):
            if name == "yaml":
                msg = "No module named 'yaml'"
                raise ImportError(msg)
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr("builtins.__import__", mock_import)

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

    def test_cli_invalid_format_argument(self):
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", "nonexistent.mp3", "--format", "invalid"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Should fail due to invalid format choice
        assert result.returncode != 0
        # argparse should show error about invalid choice
        stderr_output = result.stderr.lower()
        assert "invalid choice" in stderr_output or "error" in stderr_output

    def test_cli_invalid_output_path_empty_string(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = subprocess.run(
                [sys.executable, "-m", "audiometa", "read", str(temp_file_path), "--output", ""],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should succeed - empty output path means stdout
            assert result.returncode == 0
            assert len(result.stdout.strip()) > 0

    def test_cli_conflicting_format_options_read(self):
        with temp_file_with_metadata({}, "mp3") as temp_file_path:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "read",
                    str(temp_file_path),
                    "--format",
                    "table",
                    "--no-headers",
                    "--no-technical",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should succeed - these options are compatible
            assert result.returncode == 0
            # Table format with no headers/technical should still work
            assert len(result.stdout.strip()) > 0
