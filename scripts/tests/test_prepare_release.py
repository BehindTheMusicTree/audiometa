import subprocess
from datetime import date
from pathlib import Path

import pytest
from prepare_release import next_version, run

PYPROJECT = """[project]
name = "demo"
version = "1.4.4"

[tool.bumpversion]
current_version = "1.4.4"
"""

CHANGELOG = """# Changelog

## [Unreleased]

### Fixed

- Something new

## [1.4.4] - 2026-09-11

### Fixed

- Older
"""


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def _write_project(root: Path, changelog: str = CHANGELOG) -> None:
    (root / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    (root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    empty_config = tmp_path / "gitconfig"
    empty_config.write_text("", encoding="utf-8")
    for key, value in {
        "GIT_CONFIG_GLOBAL": str(empty_config),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }.items():
        monkeypatch.setenv(key, value)

    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    origin.mkdir()
    work.mkdir()
    _git(origin, "init", "--bare", "-b", "main")
    _git(work, "init", "-b", "main")
    _git(work, "remote", "add", "origin", str(origin))
    _write_project(work)
    _git(work, "add", ".")
    _git(work, "commit", "-m", "initial")
    _git(work, "push", "-u", "origin", "main")
    return work


@pytest.mark.unit
class TestPrepareRelease:
    @pytest.mark.parametrize(
        ("current", "part", "expected"),
        [
            ("1.4.4", "patch", "1.4.5"),
            ("1.4.4", "minor", "1.5.0"),
            ("1.4.4", "major", "2.0.0"),
            ("1.9.9", "minor", "1.10.0"),
        ],
    )
    def test_next_version(self, current: str, part: str, expected: str):
        assert next_version(current, part) == expected

    @pytest.mark.parametrize("version", ["1.5", "v1.5.0", "1.4.4", "1.4.3", "1.4.4.1"])
    def test_invalid_or_non_greater_version_is_rejected_before_writing(self, tmp_path: Path, version: str):
        _write_project(tmp_path)

        with pytest.raises(SystemExit):
            run(tmp_path, None, version, push=False)

        assert (tmp_path / "pyproject.toml").read_text(encoding="utf-8") == PYPROJECT
        assert (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8") == CHANGELOG

    def test_empty_unreleased_is_rejected_before_writing(self, tmp_path: Path):
        empty = CHANGELOG.replace("### Fixed\n\n- Something new\n\n", "", 1)
        _write_project(tmp_path, empty)

        with pytest.raises(SystemExit, match="nothing to release"):
            run(tmp_path, "patch", None, push=False)

        assert (tmp_path / "pyproject.toml").read_text(encoding="utf-8") == PYPROJECT
        assert (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8") == empty

    def test_missing_part_and_version_is_rejected(self, tmp_path: Path):
        _write_project(tmp_path)

        with pytest.raises(SystemExit, match="Provide part"):
            run(tmp_path, None, None, push=False)

    def test_release_is_committed_on_a_branch_without_tag_or_main_change(self, repo: Path):
        main_before = _git(repo, "rev-parse", "main")

        branch = run(repo, "minor", None, push=False)

        assert branch == "chore/release-1.5.0"
        assert _git(repo, "rev-parse", "--abbrev-ref", "HEAD") == branch
        assert _git(repo, "log", "-1", "--format=%s") == "chore: prepare release 1.5.0"
        assert _git(repo, "rev-parse", "main") == main_before
        assert _git(repo, "rev-parse", "origin/main") == main_before
        assert _git(repo, "tag", "--list") == ""
        assert _git(repo, "status", "--porcelain", "--untracked-files=no") == ""
        pyproject = (repo / "pyproject.toml").read_text(encoding="utf-8")
        assert pyproject.count('version = "1.5.0"') == 2
        assert f"## [1.5.0] - {date.today().isoformat()}" in (repo / "CHANGELOG.md").read_text(encoding="utf-8")

    def test_release_refuses_when_not_on_main(self, repo: Path):
        _git(repo, "checkout", "-b", "feature/other")

        with pytest.raises(SystemExit, match="current branch is feature/other"):
            run(repo, "patch", None, push=False)

        assert (repo / "pyproject.toml").read_text(encoding="utf-8") == PYPROJECT

    def test_release_refuses_dirty_tracked_files(self, repo: Path):
        (repo / "pyproject.toml").write_text(PYPROJECT + "\n# local edit\n", encoding="utf-8")

        with pytest.raises(SystemExit, match="uncommitted changes"):
            run(repo, "patch", None, push=False)

    def test_release_refuses_when_main_is_behind_origin(self, repo: Path, tmp_path: Path):
        other = tmp_path / "other"
        _git(tmp_path, "clone", str(tmp_path / "origin.git"), str(other))
        (other / "extra.txt").write_text("x", encoding="utf-8")
        _git(other, "add", ".")
        _git(other, "commit", "-m", "advance")
        _git(other, "push", "origin", "main")

        with pytest.raises(SystemExit, match="differs from origin/main"):
            run(repo, "patch", None, push=False)
