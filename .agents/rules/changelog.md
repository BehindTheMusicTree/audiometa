# Changelog

Release Please generates versioned release notes from conventional PR titles. Describe user-visible changes with a `feat:` or `fix:` title. Mark a breaking change with `!` and explain the migration in the PR description.

`CHANGELOG.md` has one level-two heading per release in descending version order. Generated headings link to the GitHub comparison and historical headings use plain bracketed versions. Run `python scripts/verify_changelog.py` after editing the file.

See [CONTRIBUTING.md](../../CONTRIBUTING.md#7-releasing-for-maintainers) for the automated release process.
