---
description: How to produce and update demo videos with VHS
paths:
  - "**/*.tape"
  - "**/demo*.py"
  - "**/VHS*.md"
  - "**/DEMO*.md"
  - "docs/demos/**"
---

# Demo Videos (VHS)

Demo videos are produced with [VHS](https://github.com/charmbracelet/vhs) from declarative `.tape` files. Follow the documented workflow so demos stay reproducible.

## Canonical docs

- **Usage and install**: `VHS_DEMO_README.md` (root)
- **Install/troubleshooting**: `DEMO_INSTALLATION.md` (root)
- **Demo asset and tweet copy**: `DEMO_VIDEOS_README.md`, `TWITTER_POST.md` (root)

## Workflow

1. **Dependencies (macOS)**: `bash scripts/install-demo-dependencies-macos.sh` (VHS, ttyd, ffmpeg; fixes libvpx issues).
2. **Activate venv** before running VHS so the tape uses the project Python: `source .venv/bin/activate`.
3. **Record from a tape**: `vhs <path/to/file>.tape` (e.g. `vhs audiometa_demo.tape` or `vhs docs/demos/tapes/get_full_metadata.tape`). Tapes in `docs/demos/tapes/` use the tracked asset `docs/demos/sample.mp3`.
4. **Preview**: `vhs <file>.tape --preview`.

## When editing demos

- **Authoring .tape files**: For best practices (length, readability, timing, one feature per tape), see `.claude/rules/demo-tape-authoring.md`.
- **New or changed tapes**: Prefer `.tape` in repo root for main demos; use `docs/demos/tapes/` for doc-specific demos. Set `Output docs/demos/output/<name>.gif` (or `.mp4`) so generated files go in the dedicated output dir. For read/unified demos, include `--color` in CLI commands so output is colorized in the video.
- **Demo scripts** (e.g. `scripts/demo_repl.py`): Keep them minimal and stable; tapes depend on their output.
- **Docs**: If you change how demos are installed or run, update `VHS_DEMO_README.md` and/or `DEMO_INSTALLATION.md` so agents and contributors stay aligned.

## Generated outputs

GIFs/MP4s go in `docs/demos/output/` (gitignored). Source tapes and `docs/demos/sample.mp3` are tracked. Article demos under `content/articles/<name>/` use per-article `output/` for GIFs, MP4s, and ffmpeg intermediates (gitignored). **Tracked audio for that article’s demos** can live in **`content/articles/<article>/samples/`** (whitelisted names: `sample.mp3`, `sample.flac`, `sample.wav` — each article is independent, not a single global “canonical” set). Do not leave those loose at the article root. Also track tapes, top-level `.md`, `.sh`, `.py`; **do not commit** ad hoc `demo_*` copies or other loose binaries. See `.gitignore` for patterns.
