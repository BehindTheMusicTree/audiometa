#!/bin/bash
# Fix trailing blank lines in shell scripts
# Ensures shell scripts end with exactly one newline (POSIX compliant)
# Automatically removes trailing blank lines

for file in "$@"; do
    if [ ! -f "$file" ]; then
        continue
    fi

    # Use Python to remove trailing blank lines
    python3 << EOF
from pathlib import Path

file_path = Path("$file")
if file_path.exists():
    content = file_path.read_bytes()
    # Remove trailing blank lines (multiple \n at end)
    while content.endswith(b'\n\n'):
        content = content[:-1]  # Remove one trailing newline
    # Ensure file ends with exactly one newline
    if content and not content.endswith(b'\n'):
        content += b'\n'
    elif not content:
        content = b'\n'
    file_path.write_bytes(content)
EOF
done

exit 0
