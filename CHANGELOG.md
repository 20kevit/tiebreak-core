# Changelog

All notable changes to `tiebreak-core` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Ruleset versions (e.g. `legacy-0.1.0`, `fide-2026`) are independent of
package versions — see `docs/VERSIONING.md`. A frozen ruleset's outputs
never change across package releases.

## [Unreleased]

Added:

- Ruleset `fide-2024` (implemented): FIDE-correct engine for individual
  Swiss tournaments from the fully-retrieved 2024 C.07 text — Article 16
  categories/adjusted scores/dummy rule/cut exception, Cut/Median
  modifiers, SB-C1/PS-C1/ARO-C1, AOB, Fore Buchholz, over-the-board
  Type-B semantics, gap-filled Progressive, Koya on maximum-possible
  threshold. New criteria: `sonneborn_berger_cut1`, `progressive_cut1`,
  `aro_cut1`, `aob`, `fore_buchholz`, `won`, `rounds_elected`. New error:
  `UnsupportedCriterionError`. Strict path dispatches per ruleset;
  uncategorized `-1` rounds are rejected under fide-2024. Corpus case
  `FIDE2024-SWISS5-ART16` (VERIFIED, hand-computed). See ADR-007.
- Explicit game-kind taxonomy (`GAME_KINDS`, `normalize_kind()`):
  `played`, `pairing_bye`, `forfeit_win`, `forfeit_loss`,
  `requested_bye`, `unplayed` (legacy generic), `absent`. Additive:
  `GameRecord.kind` defaults to unspecified, legacy calculators ignore
  it (values byte-identical, proven by tests), strict path validates
  vocabulary + kind/opponent consistency. See ADR-006.
- Corpus input examples for Article 16 categories and the DE
  mini-table (PENDING execution; kind vocabulary schema-checked).

- `median_buchholz_2` criterion (FIDE Median-2, BH-M2, C.07 §14):
  Buchholz minus two highest and two lowest opponent scores, with a
  documented fallback to full Buchholz for fewer than 5 opponent scores.
  New id only — no existing output changed. Covered by unit tests and a
  VERIFIED corpus case (`FIDE-MEDIAN2-TRIM`).

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
