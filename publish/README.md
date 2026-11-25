# Published docs bundle

The file `docs-bundle.json` in this directory is built by `scripts/build_docs_bundle.py`. It contains selected Markdown docs from `docs/` (see `DOC_SLUGS` in the script) with internal links rewritten to `/docs/<slug>` for consumption by the [Audiometa frontend](https://github.com/BehindTheMusicTree/audiometa-frontend).

**Published location (canonical URL):** The bundle is committed in this repo and consumed at the organization/repo path. The frontend should fetch it from a stable URL, for example:

- **Branch:** `https://raw.githubusercontent.com/BehindTheMusicTree/audiometa/main/publish/docs-bundle.json`
- **Tag (e.g. release):** `https://raw.githubusercontent.com/BehindTheMusicTree/audiometa/v1.3.0/publish/docs-bundle.json`

Using a tag URL is recommended for production so the frontend gets a pinned version. The path `publish/` is used (not `dist/`) because `dist/` is reserved for Python package build output (wheels, sdists) and is gitignored.

The frontend fetches this bundle at build time and renders the content under its `/docs` section for SEO and AEO. A demo web app is available at [audiometa.themusictree.org](https://audiometa.themusictree.org).

## Rebuilding

- **Locally**: From the repo root, run `python3 scripts/build_docs_bundle.py`.
- **CI**: The **Publish docs bundle** workflow builds from `main` after PyPI publication succeeds. Maintainers can also run it manually on `main`.

When the bundle changes, the workflow uses the repository-scoped Release PR App to update `chore/update-docs-bundle` and open a PR to `main`. Merge the PR after its checks pass to update the canonical bundle URL.
