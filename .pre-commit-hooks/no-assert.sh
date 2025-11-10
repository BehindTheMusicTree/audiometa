#!/bin/bash
# Check for assert statements in production code (test files are allowed to use assert)
# Assert statements should be replaced with proper error handling in production code

found_asserts=0

for file in "$@"; do
  # Skip test files - assert statements are allowed in tests
  if [[ "$file" =~ (test/|tests/) ]]; then
    continue
  fi

  # Use Python to find assert statements (excluding docstrings/comments)
  python3 << EOF
import ast
import sys

try:
    with open("$file", "r") as f:
        lines = f.readlines()
        content = ''.join(lines)

    # Parse to find assert statements
    tree = ast.parse(content, filename="$file")
    assert_found = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            lineno = node.lineno
            # Check if it's in a docstring or comment
            line = lines[lineno - 1]
            if '"""' in line or "'''" in line or line.strip().startswith('#'):
                continue

            if not assert_found:
                print(f"Error: Found assert statements in: $file")
                assert_found = True

            print(f"  Line {lineno}: {line.strip()}")

    if assert_found:
        sys.exit(1)
    else:
        sys.exit(0)
except SyntaxError:
    # If file has syntax errors, skip it (will be caught by other linters)
    sys.exit(0)
except Exception:
    # Fallback: use grep to find asserts
    import subprocess
    result = subprocess.run(['grep', '-n', '^[[:space:]]*assert[[:space:]]', "$file"],
                          capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Error: Found assert statements in: $file")
        print(result.stdout)
        sys.exit(1)
    sys.exit(0)
EOF

  if [ $? -ne 0 ]; then
    found_asserts=1
  fi
done

if [ $found_asserts -eq 1 ]; then
  echo ""
  echo "❌ Assert statements are not allowed. Use proper error handling with exceptions instead."
  echo "Replace assert statements with appropriate exceptions (ValueError, TypeError, etc.)."
  exit 1
fi

exit 0
