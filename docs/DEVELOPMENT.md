# Development and testing

## Setup

```bash
pip install -e .            # zero runtime dependencies
python -m pytest tests -q   # full suite (see below)
```

Supported interpreters: Python 3.10, 3.11, 3.12 (CI matrix in
`.github/workflows/ci.yml`). The library is stdlib-only; development
tooling (`build`, `twine`) is used from isolated environments, never
added to project dependencies.

## Test suite layout

| File(s) | What it pins |
|---|---|
| `test_calculators.py`, `test_fide2024.py`, `test_fide2026.py`, `test_ratings.py` | Unit behavior incl. zero/edge inputs |
| `test_legacy_frozen.py`, `tests/data_goldens.json` | Frozen legacy outputs (byte-identical forever) |
| `test_corpus.py`, `test_conformance.py`, `tests/corpus/` | Official FIDE worked values (each case names its source) |
| `test_differential.py`, `tests/oracle/` | Independent-oracle comparison (documented scope skips only) |
| `test_modifiers.py`, `test_team.py`, `test_policy_scoring.py` | Generic modifier machine, team domain, policy/scoring models |
| `test_direct.py`, `test_ranking.py`, `test_gamekind.py` | DE stages, ordering, game-kind taxonomy |
| `test_strict.py`, `test_rulesets.py` | Validation boundary, ruleset contracts |
| `test_examples.py`, `examples/*.py` | Every user-facing example executes in CI |
| `test_benchmarks.py` | Anti-blowup bounds (individual 100/500/2000, descriptors, teams) |

Skips are legitimate differential-harness scope guards, each with a
recorded reason (`pytest -rs` shows them). Failures are never
converted to skips; assertions are never weakened to obtain green CI.

## Conventions for contributors

- Frozen rulesets (`legacy-0.1.0`, `fide-2024`) never change outputs:
  corrections land as new code paths / new ruleset ids (see
  `docs/VERSIONING.md`). Golden + corpus tests enforce this.
- New criteria: pure function + identifier + FIDE reference + unit
  tests + corpus case where sources allow + CHANGELOG entry.
- Evidence discipline: label `PRIMARY_NORMATIVE` /
  `OFFICIAL_VALUE` / `INDEPENDENT_ORACLE` / `PROJECT_DERIVED`
  honestly — never upgrade an interpretation into an official value.
- No new runtime dependencies without strong, recorded justification
  (stdlib-first is a feature).
- Every user-facing example must execute (`tests/test_examples.py`).

## Packaging and release process

See `docs/RELEASING.md` (build, artifact inspection, clean-install
validation, PyPI notes, version policy).
