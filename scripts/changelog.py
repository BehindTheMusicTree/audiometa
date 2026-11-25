"""Parse and validate generated and historical CHANGELOG.md sections."""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import pairwise

VERSION_HEADER = re.compile(
    r"^## \[(\d+)\.(\d+)\.(\d+)\](?: - \d{4}-\d{2}-\d{2}|\(https://[^()\s]+\) \(\d{4}-\d{2}-\d{2}\))$"
)
FENCE = "```"

Version = tuple[int, int, int]


@dataclass(frozen=True)
class Section:
    heading: str
    body: str

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


def parse(text: str) -> Changelog:
    """Split on level-two headings outside fenced code blocks."""
    preamble: list[str] = []
    headings: list[str] = []
    bodies: list[list[str]] = []
    in_fence = False

    for line in text.splitlines(keepends=True):
        heading = line.rstrip("\r\n")
        if heading.strip().startswith(FENCE):
            in_fence = not in_fence
        elif not in_fence and heading.startswith("## "):
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


def validate(changelog: Changelog) -> list[str]:
    """Return errors for invalid headings or releases out of order."""
    if not changelog.sections:
        return ["No released version sections found."]

    errors: list[str] = []
    versions = []
    for line, section in zip(_heading_lines(changelog), changelog.sections, strict=True):
        version = section.version
        if version is None:
            errors.append(f"Line {line}: expected a versioned release heading, got {section.heading!r}.")
        else:
            versions.append((line, version))

    for (line, newer), (next_line, older) in pairwise(versions):
        if newer <= older:
            errors.append(f"Version order: release on line {line} must be strictly newer than line {next_line}.")

    return errors
