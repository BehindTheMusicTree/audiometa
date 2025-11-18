"""Utility functions for handling mutagen exceptions."""

from audiometa.exceptions import FileCorruptedError


def handle_mutagen_exception(operation: str, file_path: str, exception: Exception) -> None:
    """Handle exceptions from mutagen operations.

    Re-raises standard I/O exceptions as-is and converts other exceptions
    (including mutagen-specific ones) to FileCorruptedError.

    Args:
        operation: Description of the operation being performed (e.g., "save metadata", "extract RIFF metadata from")
        file_path: Path to the file being operated on
        exception: The exception that was raised

    Raises:
        IOError, OSError, PermissionError: Re-raised as-is for standard I/O errors
        FileCorruptedError: Raised for mutagen-specific or other unexpected exceptions
    """
    if isinstance(exception, IOError | OSError | PermissionError):
        raise exception
    msg = f"Failed to {operation} {file_path}: {exception!s}"
    raise FileCorruptedError(msg) from exception
