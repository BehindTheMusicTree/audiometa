#!/usr/bin/env python3
"""Verify CHANGELOG.md layout for prepare_release.py and Keep a Changelog ordering."""

from __future__ import annotations

import sys
from pathlib import Path

from changelog import parse, validate


def verify_changelog(path: Path) -> list[str]:
    """Return list of error messages; empty means OK."""
    return validate(parse(path.read_text(encoding="utf-8")))


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    changelog = root / "CHANGELOG.md"
    if not changelog.is_file():
        sys.stderr.write(f"Not found: {changelog}\n")
        sys.exit(2)
    errs = verify_changelog(changelog)
    if errs:
        sys.stderr.write("CHANGELOG.md integrity check failed:\n")
        for e in errs:
            sys.stderr.write(f"  - {e}\n")
        sys.exit(1)
    sys.stdout.write("CHANGELOG.md OK\n")


if __name__ == "__main__":
    main()
