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
Examples: `legacy-0.1.0` (implemented, frozen), `fide-2024`
(implemented, frozen outputs), `fide-2026` (implemented since 0.7.0:
Swiss core + RR mode + TPN/RTNG terminals + /P flag; STD/team/16.6
still out — see the requirements matrix for exact scope).

Rules:

- A ruleset's outputs NEVER change across package releases. If an
  official rule correction is needed, it ships as a NEW ruleset id with
  NEW code paths — never by editing the old behavior in place.
- Pre-1.0 exception (applied in 0.9.0 for F1/F2/F3): correctness fixes
  to experimental, unadopted rulesets may change outputs in place
  when the previous behavior was demonstrably incorrect, the
  correction is documented with before/after values, tests are
  updated, and the package MINOR version changes. Rationale: new-id
  proliferation for days-old unadopted rulesets harms consumers more
  than a documented correction. This exception EXPIRES at 1.0.
- Post-1.0 rule: published rulesets are frozen. Any future official
  correction ships as a NEW ruleset id (see above); output-changing
  edits to a published ruleset id are forbidden (MAJOR-level breach).
- Pre-publication correction F4 (1.2.0, sole exception): the DE/EDE
  mini-table order-dependence fix (see CHANGELOG F4) edited
  `fide-2024`/`fide-2026` in place because (a) the old behavior
  contradicted the documented algorithm and determinism contract,
  (b) every pinned and official value is byte-identical before/after
  (proven by running the full suite under both implementations), and
  (c) no PyPI publication and no adopted consumer of 1.x outputs
  existed yet. After PyPI publication this exception path is closed:
  the freeze is absolute.
- 1.3.0 corrections R1/R2 (2026-10-27): two bug fixes to code paths
  that contradicted their own documented contract, both reproduced
  against the authoritative C.07 text. R1 (descriptor ruleset dispatch)
  edited no engine — the `fide-2024` descriptor path was misrouting to
  the `fide-2026` modifier machine and now returns the value the
  `fide-2024` named id always returned, so no ruleset output moves. R2
  (round-robin REP, §7.6/§15.2) does move `fide-2026` RR-mode output,
  but only for events that combine `mode="round_robin"` with a forfeit
  loss, and only toward the regulations the module already documented
  (`docs/FIDE_2026_DIFF.md` D12). Both are recorded with before/after
  values in `CHANGELOG.md`. A maintainer who treats the published
  `fide-2026` freeze as absolute may instead cut a new ruleset id or a
  MAJOR release for R2; the correction is re-derivable either way.
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
