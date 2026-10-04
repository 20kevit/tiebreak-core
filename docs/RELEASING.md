# Packaging and release process

## Build

```bash
python -m build --outdir dist/
```

Produces `tiebreak_core-<version>.tar.gz` (sdist) and
`tiebreak_core-<version>-py3-none-any.whl` (wheel). Expected
contents:

- sdist: `LICENSE`, `README.md`, `pyproject.toml`, `src/tiebreak_core/`
  (incl. `py.typed`), `tests/`.
- wheel: `tiebreak_core/` package (incl. `py.typed`) +
  `dist-info/licenses/LICENSE`. No tests, no caches, no `.git`.

Stale local `dist/` artifacts from previous versions are build
leftovers (gitignored) — remove before rebuilding for inspection.

## Pre-release validation checklist

1. `python -m pytest tests -q` — full suite green, no unexplained skips.
2. `twine check dist/*` — README renders for PyPI (run `twine` from
   an isolated env; it is not a project dependency).
3. Wheel clean-install: fresh venv → `pip install dist/*.whl` →
   `import tiebreak_core`, version check, representative API smoke
   (individual + team + descriptor).
4. Sdist clean-install: fresh venv → `pip install dist/*.tar.gz` →
   same smoke test. Confirms no undeclared build/runtime dependency.
5. `git status` clean, `main` pushed, annotated version tag pushed.
6. `CHANGELOG.md` entry present; `docs/VERSIONING.md` policy honored.

## Version policy (summary)

- Package versions follow semver (`docs/VERSIONING.md`).
- Ruleset versions (`legacy-0.1.0`, `fide-2024`, `fide-2026`) are
  independent of package versions. A frozen ruleset's outputs never
  change across package releases; output-changing corrections require
  new ruleset ids.
- Do not bump the package version for documentation-only changes.

## PyPI notes

- Name: `tiebreak-core`. Requires Python `>=3.10`. Zero dependencies.
- License metadata: MIT (+ classifier). Keywords and project URLs
  live in `pyproject.toml` (only URLs that exist are listed).
- Publication itself is a maintainer action outside this checklist
  and requires explicit authorization; this repository is kept
  **PyPI-ready**, not auto-published.
