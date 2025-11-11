#!/usr/bin/env python3
"""Fix long comment lines by wrapping them to fit within the line length limit.

This script processes Python files and wraps long comment lines (starting with #)
to ensure they don't exceed the specified line length.
"""

import re
import sys
from pathlib import Path


def wrap_comment_line(line: str, max_length: int = 120, indent: int = 0) -> list[str]:
    """Wrap a long comment line into multiple lines.

    Args:
        line: The comment line to wrap
        max_length: Maximum line length
        indent: Number of spaces to indent continuation lines

    Returns:
        List of wrapped lines
    """
    # Remove leading whitespace and comment marker
    stripped = line.lstrip()
    if not stripped.startswith("#"):
        return [line]

    # Extract the comment content (everything after #)
    comment_content = stripped[1:].lstrip()
    if not comment_content:
        return [line]

    # Calculate available space for content (account for # and spacing)
    # Format: <indent># <content>
    available_length = max_length - indent - 2  # -2 for "# "

    if len(comment_content) <= available_length:
        return [line]

    # Split into words
    words = comment_content.split()
    wrapped_lines = []
    current_line = " " * indent + "#"

    for word in words:
        # Check if adding this word would exceed the limit
        potential_line = current_line + (" " if current_line.strip() != "#" else "") + word
        if len(potential_line) <= max_length:
            current_line = potential_line
        else:
            # Start a new line
            if current_line.strip() != "#":
                wrapped_lines.append(current_line)
            current_line = " " * indent + "# " + word

    # Add the last line
    if current_line.strip() != "#":
        wrapped_lines.append(current_line)

    return wrapped_lines if wrapped_lines else [line]


def process_file(file_path: Path, max_length: int = 120) -> bool:
    """Process a Python file and wrap long comment lines.

    Returns:
        True if file was modified, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        new_lines = []
        modified = False

        for line in lines:
            # Calculate current indent
            indent = len(line) - len(line.lstrip())

            # Check if line is too long and is a comment
            if len(line) > max_length and line.strip().startswith("#"):
                wrapped = wrap_comment_line(line, max_length, indent)
                if len(wrapped) > 1:
                    new_lines.extend(wrapped)
                    modified = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        if modified:
            file_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: fix-long-comments.py <file1> [file2] ...", file=sys.stderr)
        sys.exit(1)

    max_length = 120
    modified_files = []

    for file_path_str in sys.argv[1:]:
        file_path = Path(file_path_str)
        if file_path.exists() and file_path.suffix == ".py":
            if process_file(file_path, max_length):
                modified_files.append(file_path)

    if modified_files:
        print(f"Fixed long comment lines in: {', '.join(str(f) for f in modified_files)}")
        sys.exit(1)  # Exit with error to indicate files were modified

    sys.exit(0)


if __name__ == "__main__":
    main()

