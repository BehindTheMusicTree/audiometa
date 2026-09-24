# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

AudioMeta Python is a library and CLI (`audiometa`) for reading, writing, and deleting audio file metadata (MP3, FLAC, WAV) across formats (ID3v1, ID3v2, Vorbis, RIFF). No web services or databases—just Python + system CLI tools.

### Virtual environment

Always activate before running any command:

```bash
source .venv/bin/activate
```

Before every commit, run full hooks with:

```bash
pre-commit run --all-files
```

### System dependencies

The `flac` apt package (CLI tools) is separate from `libflac12t64` (library). The install script (`scripts/install-system-dependencies-ubuntu.sh`) may install only the library; verify `flac` and `metaflac` are on PATH after running it. If missing, install explicitly: `sudo apt-get install -y flac`.

Pre-commit hooks require `shellcheck` and `pwsh` (PowerShell). These are installed via the `lint` category: `bash scripts/install-system-dependencies-ubuntu.sh lint`. Cursor Cloud agents on Ubuntu 24.04 install these automatically via `.cursor/environment.json` (`scripts/install-cursor-cloud-dependencies.sh`). If you only need Python linting, run `ruff`, `mypy`, and `isort` directly instead of `pre-commit run --all-files`.

### Key commands

See `CONTRIBUTING.md` for full details. Quick reference:

- **Lint**: `ruff check audiometa/` / `mypy --follow-imports=normal audiometa/ --exclude audiometa/test/` / `isort --check-only --profile black --line-length=120 audiometa/`
- **Test**: `pytest` (all 1665 tests) / `pytest -m unit` / `pytest -m integration` / `pytest -m e2e`
- **CLI**: `audiometa read <file>` / `audiometa write <file> --title "..." --artist "..."` / `audiometa delete <file>`

### Changelog

When you change production code under `audiometa/`, the CLI, or user-visible behavior, update `CHANGELOG.md` in the `## [Unreleased]` section in the same work. Before finishing, confirm `[Unreleased]` matches what you changed. After any substantive edit to `CHANGELOG.md`, run `python scripts/verify_changelog.py` (layout must match `prepare_release.py`; see `.claude/rules/changelog.md`). See [DEVELOPMENT.md — Changelog and `[Unreleased]`](DEVELOPMENT.md#changelog-and-unreleased).

### Pull request descriptions

When asked for a PR description, write it to **`.github/pr_descriptions/PR_DESCRIPTION_<TOPIC>.md`** (gitignored); do not rely on chat-only text. See `.claude/rules/pr-descriptions.md` and use `.github/pr_descriptions/pull_request_template.md` for sections.

### Demo videos

Demos are generated with [VHS](https://github.com/charmbracelet/vhs) from `.tape` files. See `VHS_DEMO_README.md` and `DEMO_INSTALLATION.md` for full instructions. Quick path: install deps (macOS) with `bash scripts/install-demo-dependencies-macos.sh`, activate venv, then run `vhs <path/to/tape>.tape` (e.g. `vhs audiometa_demo.tape` or `vhs docs/demos/tapes/get_full_metadata.tape`). When editing tapes or demo workflow, follow `.claude/rules/demo-videos.md`; for authoring .tape content for social media demos, follow `.claude/rules/demo-tape-authoring.md`.

### Gotchas

- `python3.12-venv` must be installed (`sudo apt-get install -y python3.12-venv`) before creating `.venv`.
- `core.hooksPath` git config may block `pre-commit install`; unset it first: `git config --unset-all core.hooksPath`.
- Test audio files in `audiometa/test/assets/` are generated via `create_test_files.py`, not checked in as binaries.
- `numpy==2.3.4` is a dev dependency (for `soundfile` test file generation); it is not a production dependency.
