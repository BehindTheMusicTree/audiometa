#!/bin/bash
# Check for trailing blank lines in shell scripts
# Ensures shell scripts end with exactly one newline (POSIX compliant)
# Exits with code 1 if files have trailing blank lines, 0 if all are correct

has_errors=0

for file in "$@"; do
    if [ ! -f "$file" ]; then
        continue
    fi

    # Use Python to check if file ends with \n\n (two newlines)
    python3 << EOF
from pathlib import Path
import sys

file_path = Path("$file")
if file_path.exists():
    content = file_path.read_bytes()
    if content.endswith(b'\n\n'):
        print(f"Error: {file_path} has trailing blank lines")
        sys.exit(1)
sys.exit(0)
EOF

    if [ $? -ne 0 ]; then
        has_errors=1
    fi
done

if [ $has_errors -eq 1 ]; then
    exit 1
fi

exit 0
