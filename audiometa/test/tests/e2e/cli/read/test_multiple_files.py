import json
import subprocess
import sys

import pytest

from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.e2e
class TestCLIReadMultipleFiles:
    def test_cli_read_multiple_files(self):
        with (
            temp_file_with_metadata({"title": "File One"}, "mp3") as file1,
            temp_file_with_metadata({"title": "File Two"}, "mp3") as file2,
        ):
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "read",
                    str(file1),
                    str(file2),
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            # When reading multiple files, each file outputs a separate JSON object
            # JSON objects can span multiple lines, so we need to parse them properly
            output = result.stdout.strip()
            if output:
                # Try to parse the first complete JSON object
                # Find the first complete JSON object by counting braces
                brace_count = 0
                start_idx = 0
                for i, char in enumerate(output):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            # Found complete JSON object
                            first_json_str = output[start_idx : i + 1]
                            data = json.loads(first_json_str)
                            assert isinstance(data, dict)
                            assert "unified_metadata" in data or "metadata_format" in data
                            break

    def test_cli_read_multiple_files_with_continue_on_error(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.mp3"
        with temp_file_with_metadata({"title": "Valid File"}, "mp3") as valid_file:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "audiometa",
                    "read",
                    str(nonexistent_file),
                    str(valid_file),
                    "--continue-on-error",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0
            # When reading multiple files, each file outputs a separate JSON object
            # JSON objects can span multiple lines, so we need to parse them properly
            output = result.stdout.strip()
            if output:
                # Try to parse the first complete JSON object
                brace_count = 0
                start_idx = 0
                for i, char in enumerate(output):
                    if char == "{":
                        if brace_count == 0:
                            start_idx = i
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            # Found complete JSON object
                            try:
                                first_json_str = output[start_idx : i + 1]
                                data = json.loads(first_json_str)
                                assert isinstance(data, dict)
                                break
                            except json.JSONDecodeError:
                                continue

    def test_cli_read_glob_pattern(self, tmp_path):
        # Use a dedicated temp directory to avoid matching other temp files
        test_dir = tmp_path / "glob_test"
        test_dir.mkdir()

        with temp_file_with_metadata({"title": "Pattern File 1"}, "mp3") as file1:
            file1_name = file1.name
            test_file1 = test_dir / file1_name
            import shutil

            shutil.copy2(file1, test_file1)
            with temp_file_with_metadata({"title": "Pattern File 2"}, "mp3") as temp_file2:
                file2_name = "pattern_file_2.mp3"
                test_file2 = test_dir / file2_name
                shutil.copy2(temp_file2, test_file2)

                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "audiometa",
                        "read",
                        str(test_dir / "*.mp3"),
                        "--format",
                        "json",
                        "--continue-on-error",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert result.returncode == 0
                # When reading multiple files, each file outputs a separate JSON object
                # JSON objects can span multiple lines, so we need to parse them properly
                output = result.stdout.strip()
                if output:
                    # Try to parse the first complete JSON object
                    brace_count = 0
                    start_idx = 0
                    for i, char in enumerate(output):
                        if char == "{":
                            if brace_count == 0:
                                start_idx = i
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                # Found complete JSON object
                                first_json_str = output[start_idx : i + 1]
                                data = json.loads(first_json_str)
                                assert isinstance(data, dict)
                                break
