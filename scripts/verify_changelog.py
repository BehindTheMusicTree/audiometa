#!/usr/bin/env python3
"""Verify CHANGELOG.md layout for prepare_release.py and Keep a Changelog ordering."""

from __future__ import annotations

import re
import sys
from pathlib import Path

VERSION_HEADER = re.compile(r"^## \[(\d+)\.(\d+)\.(\d+)\] - \d{4}-\d{2}-\d{2}$")


def _parse_versions_outside_fences(lines: list[str]) -> tuple[list[int], list[tuple[int, int, int, int]]]:
    """Returns (unreleased_line_indices, version_rows as (line_1based, major, minor, patch))."""
    in_fence = False
    unreleased: list[int] = []
    versions: list[tuple[int, int, int, int]] = []

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line == "## [Unreleased]":
            unreleased.append(i)
        m = VERSION_HEADER.match(line)
        if m:
            versions.append((i, int(m.group(1)), int(m.group(2)), int(m.group(3))))
    return unreleased, versions


def verify_changelog(path: Path) -> list[str]:
    """Return list of error messages; empty means OK."""
    errors: list[str] = []
    text = path.read_text()
    lines = text.splitlines()

    unreleased_lines, version_rows = _parse_versions_outside_fences(lines)

    if len(unreleased_lines) == 0:
        errors.append("Missing exactly one '## [Unreleased]' heading (outside fenced code blocks).")
    elif len(unreleased_lines) > 1:
        errors.append(
            f"Found {len(unreleased_lines)} '## [Unreleased]' headings (lines {unreleased_lines}); "
            "expected exactly one."
        )

    if not version_rows:
        errors.append("No released version sections found matching '## [X.Y.Z] - YYYY-MM-DD'.")
        return errors

    if unreleased_lines:
        u = unreleased_lines[0]
        first_v_line, *_ = version_rows[0]
        if first_v_line < u:
            errors.append(
                f"First version section (line {first_v_line}) appears before '## [Unreleased]' (line {u}). "
                "Put '## [Unreleased]' first, then the newest '## [X.Y.Z] - date', then older versions "
                "(see .claude/rules/changelog.md and scripts/prepare_release.py)."
            )

        # Verify the first ## heading after [Unreleased] (outside fences) is a version header.
        # u is a 1-based line number, so lines[u-1] is [Unreleased]; the scan starts at lines[u].
        in_fence = False
        for idx in range(u, len(lines)):
            stripped = lines[idx].strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if lines[idx].startswith("## "):
                if not VERSION_HEADER.match(lines[idx]):
                    errors.append(
                        f"Line {idx + 1}: the first '## ' section after '[Unreleased]' must be a release "
                        f"header matching '## [X.Y.Z] - YYYY-MM-DD'; got: {lines[idx]!r}."
                    )
                break  # only the first ## heading matters; stop scanning

    for i in range(len(version_rows) - 1):
        _, ma, mi, pa = version_rows[i]
        _, mb, mib, pb = version_rows[i + 1]
        if (ma, mi, pa) <= (mb, mib, pb):
            errors.append(
                f"Version order: line {version_rows[i][0]} [{ma}.{mi}.{pa}] should be strictly newer than "
                f"line {version_rows[i + 1][0]} [{mb}.{mib}.{pb}] (newest release first after [Unreleased])."
            )

    prepare_release_pattern = r"(## \[Unreleased\])\n\n" r"(.*?)" r"(\n## \[\d+\.\d+\.\d+\] - \d{4}-\d{2}-\d{2})"
    if re.search(prepare_release_pattern, text, flags=re.DOTALL) is None:
        errors.append(
            "CHANGELOG.md does not match the pattern required by scripts/prepare_release.py: "
            "'## [Unreleased]' followed by optional notes, then a line '## [X.Y.Z] - YYYY-MM-DD'."
        )

    return errors


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
