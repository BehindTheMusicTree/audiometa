import re  # noqa: INP001 - This script is run directly from scripts/.
import subprocess
import sys

from changelog import Section, parse, render, validate

DOC_PATH = re.compile(r"(?:docs/[^/]+|CONTRIBUTING|DEVELOPMENT|SUPPORT)\.md")
UNIT_TEST_PATH = re.compile(r"audiometa/test/tests/unit/(?:[^/]+/)*test_[^/]+\.py")
PORTABLE_HELPERS = frozenset(
    {
        "audiometa/utils/disc_number_read.py",
        "audiometa/utils/id3v1_genre_code_map.py",
        "audiometa/utils/raw_metadata_sanitizer.py",
    }
)


def git(*args: str) -> bytes:
    return subprocess.check_output(("git", *args))


def changed_regular_files(raw_diff: bytes) -> list[str]:
    records = raw_diff.split(b"\0")
    if records.pop():
        return []
    paths = []
    for header, path in zip(records[::2], records[1::2], strict=True):
        old_mode, new_mode, old_blob, new_blob, status = header.split()
        if old_mode != b":100644" or new_mode != b"100644" or status != b"M" or old_blob == new_blob:
            return []
        paths.append(path.decode("utf-8"))
    return paths


def published_changelog(text: str) -> tuple[str, tuple[Section, ...]] | None:
    changelog = parse(text)
    if render(changelog) != text or validate(changelog):
        return None
    unreleased, *releases = changelog.sections
    if not unreleased.is_unreleased:
        return None
    return changelog.preamble, tuple(releases)


def changes_only_unreleased(before: str, after: str) -> bool:
    published = published_changelog(before)
    return published is not None and published == published_changelog(after)


def select_mode(paths: list[str]) -> str:
    if not paths:
        return "full"
    non_docs = [path for path in paths if not DOC_PATH.fullmatch(path)]
    if not non_docs:
        return "docs"
    code_paths = [path for path in non_docs if path != "CHANGELOG.md"]
    if not code_paths or not all(path in PORTABLE_HELPERS or UNIT_TEST_PATH.fullmatch(path) for path in code_paths):
        return "full"
    if "CHANGELOG.md" in non_docs:
        before = git("show", "HEAD^1:CHANGELOG.md").decode("utf-8")
        after = git("show", "HEAD:CHANGELOG.md").decode("utf-8")
        if not changes_only_unreleased(before, after):
            return "full"
    return "reduced"


def main() -> None:
    try:
        git("rev-parse", "--verify", "HEAD^2")
        diff = git(
            "diff", "--raw", "-z", "--no-abbrev", "--no-renames", "--ignore-submodules=none", "HEAD^1", "HEAD", "--"
        )
        mode = select_mode(changed_regular_files(diff))
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        sys.stderr.write(f"Unable to classify PR changes. Running the full matrix. {error}\n")
        mode = "full"
    sys.stdout.write(f"{mode}\n")


if __name__ == "__main__":
    main()
