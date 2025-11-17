#!/bin/bash
# Remove trailing blank lines from files
# Ensures files end with exactly one newline (PEP 8 / POSIX compliant)

for file in "$@"; do
    if [ ! -f "$file" ]; then
        continue
    fi

    # Read file into array (preserves empty lines)
    mapfile -t lines < "$file"

    # Remove trailing empty lines
    while [ ${#lines[@]} -gt 0 ] && [ -z "${lines[-1]}" ]; do
        unset 'lines[-1]'
    done

    # Write back with single trailing newline
    if [ ${#lines[@]} -gt 0 ]; then
        printf '%s\n' "${lines[@]}" > "$file"
    else
        # Empty file - just ensure it exists
        touch "$file"
    fi
done
