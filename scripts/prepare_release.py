#!/usr/bin/env python3
"""Update CHANGELOG and run bump-my-version for a release. Run from repo root with venv active."""

import argparse
import re
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path


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


def parse_version(v: str) -> tuple[int, int, int]:
    parts = v.split(".")
    if len(parts) != 3:
        raise ValueError(f"Expected X.Y.Z, got {v}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def next_version(current: str, part: str) -> str:
    major, minor, patch = parse_version(current)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"part must be major|minor|patch, got {part}")


def update_changelog(repo_root: Path, new_version: str, release_date: str) -> None:
    path = repo_root / "CHANGELOG.md"
    content = path.read_text()
    pattern = r"(## \[Unreleased\])\n\n" r"(.*?)" r"(\n## \[\d+\.\d+\.\d+\] - \d{4}-\d{2}-\d{2})"
    replacement = r"\1\n\n" f"## [{new_version}] - {release_date}\n\n" r"\2\3"
    new_content, n = re.subn(pattern, replacement, content, count=1, flags=re.DOTALL)
    if n != 1:
        raise SystemExit(
            "CHANGELOG.md: expected exactly one '## [Unreleased]' block followed by a version header. Check the format."
        )
    path.write_text(new_content)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update CHANGELOG with release version and date, then run bump-my-version."
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
        help="Push main and the new tag to origin after committing and tagging",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.is_file():
        raise SystemExit("Run from repository root (missing pyproject.toml).")

    verify_script = repo_root / "scripts" / "verify_changelog.py"
    subprocess.run([sys.executable, str(verify_script)], cwd=repo_root, check=True)

    project_version, bump_current_version = get_release_versions(pyproject_path)
    if project_version != bump_current_version:
        raise SystemExit(
            "Version mismatch in pyproject.toml: project.version "
            f"({project_version}) != tool.bumpversion.current_version ({bump_current_version})"
        )
    current = project_version
    if args.new_version:
        new_version = args.new_version
    elif args.part:
        new_version = next_version(current, args.part)
    else:
        raise SystemExit("Provide part (patch|minor|major) or --new-version X.Y.Z")

    release_date = date.today().isoformat()
    update_changelog(repo_root, new_version, release_date)
    subprocess.run([sys.executable, str(verify_script)], cwd=repo_root, check=True)

    cmd = [
        "bump-my-version",
        "bump",
        "--no-commit",
        "--no-tag",
        "--allow-dirty",
    ]
    if args.new_version:
        cmd += ["--new-version", new_version]
    else:
        cmd.append(args.part)

    subprocess.run(
        cmd,
        cwd=repo_root,
        check=True,
    )

    release_files = ["CHANGELOG.md", "pyproject.toml"]
    subprocess.run(
        ["pre-commit", "run", "--files"] + release_files,
        cwd=repo_root,
        check=False,
    )
    subprocess.run(
        ["git", "add"] + release_files,
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", f"chore: prepare release {new_version}"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["git", "tag", f"v{new_version}"],
        cwd=repo_root,
        check=True,
    )
    if args.push:
        subprocess.run(["git", "push", "origin", "main"], cwd=repo_root, check=True)
        subprocess.run(["git", "push", "origin", f"v{new_version}"], cwd=repo_root, check=True)
        print(f"Release {new_version} prepared and pushed.")
    else:
        print(f"Release {new_version} prepared. Push with: git push origin main && git push origin v{new_version}")


if __name__ == "__main__":
    main()
