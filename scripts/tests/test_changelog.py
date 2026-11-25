from pathlib import Path

import pytest
from changelog import parse, render, validate

REPO_ROOT = Path(__file__).resolve().parents[2]

RELEASE_HEADING = "## [1.4.5](https://github.com/example/audiometa/compare/v1.4.4...v1.4.5) (2026-10-28)"

SAMPLE = f"""# Changelog

Intro.

{RELEASE_HEADING}

### Fixed

- Something new

## [1.4.4] - 2026-09-11

### Fixed

- Newer

## [1.4.3] - 2026-09-01

### Fixed

- Older
"""


@pytest.mark.unit
class TestChangelog:
    def test_render_round_trips_real_changelog(self):
        text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        assert render(parse(text)) == text

    def test_real_changelog_is_valid(self):
        text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        assert validate(parse(text)) == []

    def test_sample_is_valid_and_has_three_sections(self):
        changelog = parse(SAMPLE)

        assert validate(changelog) == []
        assert [s.heading for s in changelog.sections] == [
            RELEASE_HEADING,
            "## [1.4.4] - 2026-09-11",
            "## [1.4.3] - 2026-09-01",
        ]

    def test_fenced_version_heading_is_not_a_section(self):
        text = SAMPLE.replace("Intro.\n", "Intro.\n\n```markdown\n## [9.9.9] - 2026-01-01\n## Notes\n```\n", 1)
        changelog = parse(text)

        assert len(changelog.sections) == 3
        assert validate(changelog) == []
        assert render(changelog) == text

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            (SAMPLE.replace(RELEASE_HEADING, "## [Unreleased]", 1), "expected a versioned release heading"),
            ("# Changelog\n\n- x\n", "No released version"),
            (SAMPLE.replace("[1.4.3]", "[1.4.5]"), "Version order"),
            (SAMPLE.replace("[1.4.3]", "[1.4.4]"), "Version order"),
            (SAMPLE.replace("- Something new", "- Something new\n\n## Notes"), "expected a versioned release heading"),
        ],
    )
    def test_validate_reports_layout_errors(self, text: str, expected: str):
        errors = validate(parse(text))

        assert any(expected in e for e in errors), errors
