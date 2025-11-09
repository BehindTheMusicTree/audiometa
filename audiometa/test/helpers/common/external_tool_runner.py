"""Unified utility for running external tools and scripts with consistent error handling."""

import subprocess
from pathlib import Path
from typing import List, Optional, Union


class ExternalMetadataToolError(Exception):
    """Exception raised when external metadata tools fail."""


def run_external_tool(
    command: List[str], tool_name: str = "external tool", check: bool = True, input: Optional[Union[str, bytes]] = None
) -> subprocess.CompletedProcess:
    """Run an external tool command with proper error handling.

    Args:
        command: List of command and arguments to execute
        tool_name: Name of the tool for error messages (e.g., "metaflac", "mid3v2")
        check: Whether to raise exception on non-zero exit code
        input: Optional input to pass to stdin

    Returns:
        subprocess.CompletedProcess: The result of the command execution

    Raises:
        ExternalMetadataToolError: If the command fails or tool is not found
    """
    try:
        text = not isinstance(input, bytes) if input is not None else True
        result = subprocess.run(command, capture_output=True, text=text, check=check, input=input)
        return result
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise ExternalMetadataToolError(f"{tool_name} failed: {e}") from e


def run_script(
    script_path: Union[str, Path], target_file: Union[str, Path], scripts_dir: Union[str, Path] = None
) -> subprocess.CompletedProcess:
    """Run a shell script with proper error handling and permissions.

    Convenience wrapper around run_external_tool for script execution.

    Args:
        script_path: Path to the script file, or script name if scripts_dir is provided
        target_file: File to pass as argument to the script
        scripts_dir: Directory containing scripts (optional, if script_path is relative)

    Returns:
        subprocess.CompletedProcess: The result of the script execution

    Raises:
        FileNotFoundError: If the script file doesn't exist
        ExternalMetadataToolError: If the script execution fails
    """
    # Resolve script path
    if scripts_dir is not None:
        full_script_path = Path(scripts_dir) / script_path
    else:
        full_script_path = Path(script_path)

    # Validate script exists
    if not full_script_path.exists():
        raise FileNotFoundError(f"Script not found: {full_script_path}")

    if not full_script_path.is_file():
        raise FileNotFoundError(f"Script is not a file: {full_script_path}")

    # Make script executable
    full_script_path.chmod(0o755)

    # Run script using the unified external tool runner
    script_name = full_script_path.name
    command = [str(full_script_path), str(target_file)]

    return run_external_tool(command, f"script {script_name}")
