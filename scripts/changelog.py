"""Parse, validate and cut releases of CHANGELOG.md (Keep a Changelog layout).

Shared by scripts/verify_changelog.py and scripts/prepare_release.py so both agree on what a valid file is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import pairwise

UNRELEASED_HEADING = "## [Unreleased]"
VERSION_HEADER = re.compile(r"^## \[(\d+)\.(\d+)\.(\d+)\] - \d{4}-\d{2}-\d{2}$")
VERSION_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
FENCE = "```"

Version = tuple[int, int, int]


class ChangelogError(Exception):
    pass


@dataclass(frozen=True)
class Section:
    heading: str
    body: str

    @property
    def is_unreleased(self) -> bool:
        return self.heading == UNRELEASED_HEADING

    @property
    def version(self) -> Version | None:
        match = VERSION_HEADER.match(self.heading)
        if match is None:
            return None
        return int(match[1]), int(match[2]), int(match[3])


@dataclass(frozen=True)
class Changelog:
    preamble: str
    sections: tuple[Section, ...]


def parse_version(value: str) -> Version:
    match = VERSION_PATTERN.match(value)
    if match is None:
        raise ValueError(f"Expected X.Y.Z (e.g. 1.3.1), got {value!r}")
    return int(match[1]), int(match[2]), int(match[3])


def format_version(version: Version) -> str:
    return ".".join(str(part) for part in version)


def _is_boundary(heading: str) -> bool:
    return heading == UNRELEASED_HEADING or VERSION_HEADER.match(heading) is not None


def parse(text: str) -> Changelog:
    """Split on '## [Unreleased]' and '## [X.Y.Z] - date' headings outside fenced code blocks."""
    preamble: list[str] = []
    headings: list[str] = []
    bodies: list[list[str]] = []
    in_fence = False

    for line in text.splitlines(keepends=True):
        heading = line.rstrip("\r\n")
        if heading.strip().startswith(FENCE):
            in_fence = not in_fence
        elif not in_fence and _is_boundary(heading):
            headings.append(heading)
            bodies.append([])
            continue
        (bodies[-1] if bodies else preamble).append(line)

    sections = tuple(Section(h, "".join(b)) for h, b in zip(headings, bodies, strict=True))
    return Changelog("".join(preamble), sections)


def render(changelog: Changelog) -> str:
    return changelog.preamble + "".join(f"{s.heading}\n{s.body}" for s in changelog.sections)


def _heading_lines(changelog: Changelog) -> list[int]:
    """1-based line number of each section heading in the rendered file."""
    line = 1 + changelog.preamble.count("\n")
    lines: list[int] = []
    for section in changelog.sections:
        lines.append(line)
        line += 1 + section.body.count("\n")
    return lines


def _stray_headings(section: Section, heading_line: int) -> list[tuple[int, str]]:
    """'## ' lines inside a section body, outside fenced code blocks, as (1-based line, text)."""
    in_fence = False
    found: list[tuple[int, str]] = []
    for offset, line in enumerate(section.body.splitlines(), start=1):
        if line.strip().startswith(FENCE):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            found.append((heading_line + offset, line))
    return found


def validate(changelog: Changelog) -> list[str]:
    """Return error messages; empty means the layout is valid."""
    errors: list[str] = []
    lines = _heading_lines(changelog)
    unreleased = [(line, s) for line, s in zip(lines, changelog.sections, strict=True) if s.is_unreleased]
    versions = [(line, s.version) for line, s in zip(lines, changelog.sections, strict=True) if s.version]

    if not unreleased:
        errors.append("Missing exactly one '## [Unreleased]' heading (outside fenced code blocks).")
    elif len(unreleased) > 1:
        errors.append(
            f"Found {len(unreleased)} '## [Unreleased]' headings (lines {[line for line, _ in unreleased]}); "
            "expected exactly one."
        )

    if not versions:
        errors.append("No released version sections found matching '## [X.Y.Z] - YYYY-MM-DD'.")
        return errors

    if unreleased:
        unreleased_line, unreleased_section = unreleased[0]
        first_version_line = versions[0][0]
        if first_version_line < unreleased_line:
            errors.append(
                f"First version section (line {first_version_line}) appears before '## [Unreleased]' "
                f"(line {unreleased_line}). Put '## [Unreleased]' first, then the newest '## [X.Y.Z] - date', "
                "then older versions (see .claude/rules/changelog.md and scripts/prepare_release.py)."
            )
        for line_number, text in _stray_headings(unreleased_section, unreleased_line)[:1]:
            errors.append(
                f"Line {line_number}: the first '## ' section after '[Unreleased]' must be a release "
                f"header matching '## [X.Y.Z] - YYYY-MM-DD'; got: {text!r}."
            )

    for (line, newer), (next_line, older) in pairwise(versions):
        if newer is not None and older is not None and newer <= older:
            errors.append(
                f"Version order: line {line} [{format_version(newer)}] should be strictly newer than "
                f"line {next_line} [{format_version(older)}] (newest release first after [Unreleased])."
            )

    return errors


def cut_release(changelog: Changelog, version: str, release_date: str) -> Changelog:
    """Move the [Unreleased] notes under a new '## [version] - release_date' section and reset [Unreleased]."""
    problems = validate(changelog)
    if problems:
        raise ChangelogError("CHANGELOG.md is invalid: " + " ".join(problems))

    new_version = parse_version(version)
    index = next(i for i, s in enumerate(changelog.sections) if s.is_unreleased)
    unreleased = changelog.sections[index]
    if not unreleased.body.strip():
        raise ChangelogError("'## [Unreleased]' is empty; there is nothing to release.")

    latest = next(v for s in changelog.sections if (v := s.version) is not None)
    if new_version <= latest:
        raise ChangelogError(f"Version {version} must be greater than the latest release {format_version(latest)}.")

    released = Section(f"## [{version}] - {release_date}", unreleased.body)
    sections = (
        *changelog.sections[:index],
        Section(UNRELEASED_HEADING, "\n"),
        released,
        *changelog.sections[index + 1 :],
    )
    result = Changelog(changelog.preamble, sections)

    problems = validate(result)
    if problems:
        raise ChangelogError("Release would produce an invalid CHANGELOG.md: " + " ".join(problems))
    return result
