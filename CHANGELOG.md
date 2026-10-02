# Changelog

All notable changes to `tiebreak-core` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Ruleset versions (e.g. `legacy-0.1.0`, `fide-2026`) are independent of
package versions — see `docs/VERSIONING.md`. A frozen ruleset's outputs
never change across package releases.

## [Unreleased]

## [0.2.0] — 2026-10-02

Added (all backwards-compatible; no legacy output changed):

- Inspectable ruleset model: `RulesetInfo`, `available_rulesets()`,
  `describe_ruleset()` (`tiebreak_core.rules`). `fide-2026` is described
  as `status="reserved"`; requesting it still raises
  `UnsupportedRulesetError`.
- `docs/VERSIONING.md`: package vs ruleset vs API version policy.
- `docs/adr/`: ADR-001 (ruleset model), ADR-002 (dual legacy+strict API),
  ADR-003 (numeric representation), ADR-004 (missing-data semantics),
  ADR-005 (registry design).
- `docs/ARCHITECTURE.md`: consolidated architectural source of truth
  (responsibilities, boundaries, lifecycle, testing, integration).
- `docs/ROADMAP.md`, `docs/MASTER_PLAN.md`: phased evolution path.
- `tests/corpus/`: FIDE conformance corpus framework (loader + schema;
  cases graded by provenance, unverified cases marked PENDING).
- Type annotations completed on all public APIs; `py.typed` marker.

## [0.1.0] — 2026-10-01

- Behavior-preserving extraction from chess-manager `domain/tiebreak/`.
- 14 calculators under frozen ruleset `legacy-0.1.0` (Direct Encounter at
  standings level is a documented `0.0` stub).
- Explicit ranking comparator (`rank_standings` / `order_ids` /
  `sort_key`); tournament seeding deliberately excluded.
- Additive strict API (`tiebreak_core.strict`) with typed errors and
  input validation; values identical to legacy by delegation.
- Registry hardening: `frozen_registry()`, `register_criterion()`
  (built-in overwrite refused), `unregister_criterion()`, `is_known()`.
- Golden fixtures (`tests/data_goldens.json`) + live old-vs-new
  conformance harness + determinism tests.
- Zero runtime dependencies; Python `>=3.10`; MIT license.
