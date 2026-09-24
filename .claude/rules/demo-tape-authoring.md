---
description: Best practices for authoring .tape files (VHS) for quick social media demos
paths:
  - "**/*.tape"
  - "docs/demos/**"
---

# VHS Tape Authoring for Social Media Demos

When writing or editing `.tape` files to produce demo videos for social posts (Mastodon, Twitter, etc.), follow these practices so demos are short, readable, and shareable.

## Length and Scope

- **Target duration**: 15–45 seconds for social. Longer demos get skipped.
- **One feature per tape**: One clear use case per tape (e.g. “read metadata as JSON”, “update title”). Split into multiple tapes if showing several features.
- **Minimal steps**: Type only the commands needed to show the feature; avoid long intros or redundant output.

## Tape Structure

- **Header**: Put `Output`, `Require`, and `Set` at the top. Use `Require audiometa` (or the relevant CLI) so the tape fails fast if the env is wrong.
- **Run from project root**: Always run `vhs` from repo root so paths resolve. Tapes assume the shell CWD is repo root.
- **Output location**: Tapes live in `docs/demos/tapes/`. Set `Output docs/demos/output/<name>.gif` (or `.mp4`) so generated files go in the dedicated output dir.
- **Audio files – social / marketing demos**: Use `docs/demos/sample.mp3` (tracked in repo; Queen track) so the video shows a clean, professional path. No setup script—the file is already there.
- **Audio files – dev-only demos**: Using `audiometa/test/assets/...` in the tape is fine when the audience is contributors; run from repo root so those paths resolve. Ensure test assets exist (e.g. `create_test_files.py`) before recording.

## Readability on Small Screens

- **FontSize**: 14–18. Use 16–18 for key demos so text is legible in feeds.
- **Width/Height**: e.g. 1200×600 or 1200×800 so content fits without tiny text.
- **Theme**: Use a consistent theme (e.g. `Set Theme "Dracula"`) for a polished look.

## Timing

- **TypingSpeed**: 40–80ms. Too fast is hard to follow; too slow feels slow in a short clip.
- **Sleep after commands**: 1–4s for simple output, 4–8s for longer output (e.g. full JSON). Avoid long idle periods.
- **Hide/Show**: Use `Hide` before setup (e.g. starting Python) and `Show` when the actual demo starts so the clip focuses on the feature.

## Long Output (viewport overflow)

If a command’s output is taller than the terminal height, it will scroll off-screen. **Standard approach**: truncate so output fits one viewport and **indicate the cut** so viewers know more output exists. Use a subshell and `echo` after `head`: `(command | head -N; echo '...')` so the last line shows `...` (e.g. `(audiometa read ... --format json --color | head -21; echo '...')`). Use `head -21` so the 22nd line is the `...` indicator; tune N to your `Set Height` and font size (~20–25 lines for 700px at 16pt). Alternatives: increase `Set Height` for that scene, or show a shorter format (e.g. table only).

## Content and Copy

- **Echo a short title** (optional): e.g. `Type "echo '=== AudioMeta – Get full metadata'"` then `Enter` and `Sleep 1s` to introduce the clip.
- **Real commands only**: Use real `audiometa` CLI or Python API calls; avoid placeholder or fake commands.
- **Stable assets**: For social demos use `docs/demos/sample.mp3` (tracked). For dev demos, test assets under `audiometa/test/assets/` are fine.
- **Colored output**: Use `--color` on `audiometa read` / `audiometa unified` in the tape so the video shows colored headers, keys, and values (e.g. `audiometa read ... --format table --color`). Plain output is the CLI default; `--color` is opt-in for demos and terminals.

## Checklist for New Social Demos

- [ ] Single, clear feature; duration ~15–45s
- [ ] `Require` the needed CLI/binary
- [ ] `Output` set to `docs/demos/output/<name>.gif` (or `.mp4`); tape file in `docs/demos/tapes/`
- [ ] FontSize 14–18; Width/Height set
- [ ] TypingSpeed and Sleep tuned so output is readable
- [ ] Commands and paths valid from project root
- [ ] For social demos: tape uses `docs/demos/sample.mp3` (tracked demo asset)
- [ ] For read/unified demos: commands include `--color` so output is colorized in the video
- [ ] Run with `vhs <file>.tape` (and `--preview` when editing); activate venv first

For workflow (install, run, preview) and where to put tapes, see `.claude/rules/demo-videos.md`. For the text of the social post (e.g. 494 char max), see `.claude/rules/mastodon-posts.md`.
