# Versioning policy

Three version axes exist. They are independent — do not confuse them.

## 1. Package version (semver)

`pyproject.toml` / `tiebreak_core.__version__`. Follows semver:

- MAJOR — breaking change to the public contract (removed/renamed
  public symbols, changed semantics of a documented API, changed a
  frozen ruleset's outputs — the latter is forbidden, see below).
- MINOR — backwards-compatible functionality (new criteria, new
  helpers, new optional parameters, new supported rulesets).
- PATCH — backwards-compatible fixes (docs, typing, performance with
  identical outputs, packaging).

## 2. Ruleset version (frozen behavior pins)

`tiebreak_core.rules` / `StandingsResult.rules_version`.
Examples: `legacy-0.1.0` (implemented, frozen), `fide-2026` (reserved).

Rules:

- A ruleset's outputs NEVER change across package releases. If an
  official rule correction is needed, it ships as a NEW ruleset id with
  NEW code paths — never by editing the old behavior in place.
- `CALCULATION_RULES_VERSION` is the default ruleset the library
  calculates under when no explicit selection is made.
- New rulesets are MINOR package changes (additive). Removing a
  ruleset is MAJOR and requires a deprecation cycle.

## 3. API generation (legacy vs strict)

- Legacy surface (`calculate`, `calculate_all`, `rank_standings`,
  mutable `TIEBREAK_REGISTRY`): frozen semantics, kept working.
- Strict surface (`tiebreak_core.strict`, `frozen_registry()`):
  fail-fast contracts, same values.
- Strictening legacy behavior (e.g. making `calculate` raise on unknown
  criteria) would be a MAJOR breaking change and is NOT planned; the
  strict surface exists precisely to avoid it.

## Practical consequences

- chess-manager should pin `tiebreak-core` by package version (or git
  tag) AND record `StandingsResult.rules_version` alongside stored
  standings for reproducibility.
- Golden fixtures are per-ruleset: `tests/data_goldens.json` pins
  `legacy-0.1.0` forever.
