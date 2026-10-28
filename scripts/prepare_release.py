#!/usr/bin/env python3
"""Prepare a release PR: cut CHANGELOG, bump the version, commit on chore/release-X.Y.Z.

Run from repo root with venv active. The tag and PyPI publish happen in CI once the PR is merged.
"""

import argparse
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

from changelog import ChangelogError, cut_release, format_version, parse, parse_version, render
from verify_changelog import verify_changelog

RELEASE_FILES = ["CHANGELOG.md", "pyproject.toml"]


def get_release_versions(pyproject: Path) -> tuple[str, str]:
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project_version = data.get("project", {}).get("version")
    if not isinstance(project_version, str):
        raise SystemExit("Could not find project.version string in pyproject.toml")
    tool_bump = data.get("tool", {}).get("bumpversion")
    if not isinstance(tool_bump, dict):
        raise SystemExit("Missing [tool.bumpversion] in pyproject.toml (bump-my-version config).")
    bump_current_version = tool_bump.get("current_version")
    if not isinstance(bump_current_version, str):
        raise SystemExit("Could not find tool.bumpversion.current_version string in pyproject.toml")
    return project_version, bump_current_version


def next_version(current: str, part: str) -> str:
    major, minor, patch = parse_version(current)
    if part == "major":
        return format_version((major + 1, 0, 0))
    if part == "minor":
        return format_version((major, minor + 1, 0))
    if part == "patch":
        return format_version((major, minor, patch + 1))
    raise ValueError(f"part must be major|minor|patch, got {part}")


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo_root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _require_branchable_main(repo_root: Path, branch: str) -> None:
    current = _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")
    if current != "main":
        raise SystemExit(f"Releases are prepared from main; current branch is {current}.")
    if _git(repo_root, "status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("Tracked files have uncommitted changes; commit or stash them first.")
    _git(repo_root, "fetch", "origin", "main")
    if _git(repo_root, "rev-parse", "HEAD") != _git(repo_root, "rev-parse", "origin/main"):
        raise SystemExit("Local main differs from origin/main; sync it first.")
    if _git(repo_root, "branch", "--list", branch):
        raise SystemExit(f"Branch {branch} already exists.")


def run(repo_root: Path, part: str | None, new_version: str | None, push: bool) -> str:
    """Prepare the release commit on a new branch and return the branch name."""
    pyproject_path = repo_root / "pyproject.toml"
    changelog_path = repo_root / "CHANGELOG.md"
    if not pyproject_path.is_file():
        raise SystemExit("Run from repository root (missing pyproject.toml).")

    project_version, bump_current_version = get_release_versions(pyproject_path)
    if project_version != bump_current_version:
        raise SystemExit(
            "Version mismatch in pyproject.toml: project.version "
            f"({project_version}) != tool.bumpversion.current_version ({bump_current_version})"
        )

    if new_version is None:
        if part is None:
            raise SystemExit("Provide part (patch|minor|major) or --new-version X.Y.Z")
        new_version = next_version(project_version, part)
    try:
        if parse_version(new_version) <= parse_version(project_version):
            raise SystemExit(f"New version {new_version} must be greater than the current version {project_version}.")
    except ValueError as err:
        raise SystemExit(str(err)) from err

    try:
        cut = cut_release(parse(changelog_path.read_text(encoding="utf-8")), new_version, date.today().isoformat())
    except ChangelogError as err:
        raise SystemExit(str(err)) from err

    branch = f"chore/release-{new_version}"
    _require_branchable_main(repo_root, branch)

    subprocess.run(
        [sys.executable, "-m", "bumpversion", "bump", "--no-commit", "--no-tag", "--allow-dirty"]
        + ["--new-version", new_version],
        cwd=repo_root,
        check=True,
    )
    changelog_path.write_text(render(cut), encoding="utf-8")
    problems = verify_changelog(changelog_path)
    if problems:
        raise SystemExit("CHANGELOG.md failed verification after release: " + " ".join(problems))

    subprocess.run([sys.executable, "-m", "pre_commit", "run", "--files", *RELEASE_FILES], cwd=repo_root, check=False)
    message = f"chore: prepare release {new_version}"
    _git(repo_root, "checkout", "-b", branch)
    _git(repo_root, "add", *RELEASE_FILES)
    _git(repo_root, "commit", "-m", message)

    if push:
        release_notes = next(s.body for s in cut.sections if s.heading.startswith(f"## [{new_version}]")).strip()
        subprocess.run(["git", "push", "-u", "origin", branch], cwd=repo_root, check=True)
        subprocess.run(
            ["gh", "pr", "create", "--base", "main", "--head", branch, "--title", message, "--body", release_notes],
            cwd=repo_root,
            check=True,
        )
        print(f"Release {new_version} prepared; merge the PR to tag and publish it.")
    else:
        print(
            f"Release {new_version} prepared on {branch}. Open the PR with: "
            f"git push -u origin {branch} && gh pr create --base main"
        )
    return branch


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cut CHANGELOG, bump the version and commit a release on a chore/release-X.Y.Z branch."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "part",
        nargs="?",
        choices=["patch", "minor", "major"],
        help="Version part to bump",
    )
    group.add_argument("--new-version", metavar="X.Y.Z", help="Explicit version (e.g. 1.3.1)")
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push the release branch and open the PR against main",
    )
    args = parser.parse_args()
    run(Path(__file__).resolve().parent.parent, args.part, args.new_version, args.push)


if __name__ == "__main__":
    main()
