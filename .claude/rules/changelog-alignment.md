---
description: Substantive changes must update CHANGELOG.md [Unreleased] in the same work
---

# Changelog alignment

When you **modify this repository** in a way that is **not purely trivial** (anything a maintainer or consumer would care about: behavior, public API of scripts, templates, CI, pins, baselines, docs that describe shipped behavior, or release/version flow):

1. **Update `CHANGELOG.md` in the same change** under **`## [Unreleased]`**, using the same categories as the rest of the file (`Added`, `Changed`, `Fixed`, etc.). Summarize what changed and why in plain language; link paths or script names when helpful.
2. **Keep it accurate**: If you touch **`.copier-answers.yml`**, standards pins, **`scripts/`** consumed by adopters, or **`.github/workflows`**, the changelog entry should reflect that so releases and migration notes stay truthful.
3. **Do not ship substantive edits without a matching `[Unreleased]` line** unless the user explicitly asked to skip the changelog (rare).

**Exempt (no changelog line required):** typo-only fixes in comments, formatting-only edits with no semantic change, or purely mechanical refactors explicitly scoped as "no changelog" by the user.

If you are **aligning another repo** to these standards, that consumer's **`CHANGELOG.md`** (or their agreed release notes) should be updated there—not only the standards repo—when your work there is user-visible.
