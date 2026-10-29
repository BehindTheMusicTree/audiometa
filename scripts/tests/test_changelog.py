from pathlib import Path

import pytest
from changelog import ChangelogError, cut_release, parse, parse_version, render, validate

REPO_ROOT = Path(__file__).resolve().parents[2]

SAMPLE = """# Changelog

Intro.

## [Unreleased]

### Fixed

- Something new

## [1.4.4] - 2026-09-11

### Fixed

- Newer

## [1.4.3] - 2026-09-01

### Fixed

- Older
"""

EMPTY_UNRELEASED = SAMPLE.replace("### Fixed\n\n- Something new\n\n", "", 1)


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
            "## [Unreleased]",
            "## [1.4.4] - 2026-09-11",
            "## [1.4.3] - 2026-09-01",
        ]

    def test_fenced_version_heading_is_not_a_section(self):
        text = SAMPLE.replace("Intro.\n", "Intro.\n\n```markdown\n## [9.9.9] - 2026-01-01\n## [Unreleased]\n```\n", 1)

        changelog = parse(text)

        assert len(changelog.sections) == 3
        assert validate(changelog) == []
        assert render(changelog) == text

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            (SAMPLE.replace("## [Unreleased]", "## Notes", 1), "Missing exactly one"),
            (SAMPLE + "\n## [Unreleased]\n", "'## [Unreleased]' headings"),
            ("# Changelog\n\n## [Unreleased]\n\n- x\n", "No released version"),
            (
                SAMPLE.replace("## [Unreleased]", "## [1.4.0] - 2026-01-01\n\n## [Unreleased]", 1),
                "appears before '## [Unreleased]'",
            ),
            (SAMPLE.replace("[1.4.3]", "[1.4.5]"), "Version order"),
            (SAMPLE.replace("[1.4.3]", "[1.4.4]"), "Version order"),
            (SAMPLE.replace("- Something new", "- Something new\n\n## Notes"), "must be a release header"),
        ],
    )
    def test_validate_reports_layout_errors(self, text: str, expected: str):
        errors = validate(parse(text))

        assert any(expected in e for e in errors), errors

    def test_cut_release_moves_unreleased_notes_under_new_version(self):
        cut = cut_release(parse(SAMPLE), "1.5.0", "2026-10-28")

        assert [s.heading for s in cut.sections] == [
            "## [Unreleased]",
            "## [1.5.0] - 2026-10-28",
            "## [1.4.4] - 2026-09-11",
            "## [1.4.3] - 2026-09-01",
        ]
        assert cut.sections[0].body == "\n"
        assert cut.sections[1].body == parse(SAMPLE).sections[0].body
        assert cut.sections[2:] == parse(SAMPLE).sections[1:]
        assert validate(parse(render(cut))) == []

    @pytest.mark.parametrize("version", ["1.4.4", "1.4.3", "0.9.0"])
    def test_cut_release_refuses_version_not_greater_than_latest(self, version: str):
        with pytest.raises(ChangelogError, match="must be greater"):
            cut_release(parse(SAMPLE), version, "2026-10-28")

    def test_cut_release_refuses_empty_unreleased(self):
        with pytest.raises(ChangelogError, match="nothing to release"):
            cut_release(parse(EMPTY_UNRELEASED), "1.5.0", "2026-10-28")

    def test_cut_release_refuses_invalid_changelog(self):
        with pytest.raises(ChangelogError, match="invalid"):
            cut_release(parse(SAMPLE.replace("[1.4.3]", "[1.4.5]")), "1.5.0", "2026-10-28")

    @pytest.mark.parametrize("version", ["1.5", "v1.5.0", "01.2.3", "1.2.3.4", "1.2.x", ""])
    def test_parse_version_rejects_malformed(self, version: str):
        with pytest.raises(ValueError, match="Expected X.Y.Z"):
            parse_version(version)

    def test_parse_version_orders_numerically(self):
        assert parse_version("1.10.0") > parse_version("1.9.9")
