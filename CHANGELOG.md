# Changelog

All notable changes to `tiebreak-core` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Ruleset versions (e.g. `legacy-0.1.0`, `fide-2026`) are independent of
package versions — see `docs/VERSIONING.md`. A frozen ruleset's outputs
never change across package releases.

## [0.6.0] — 2026-10-03

Pre-development readiness gate (no calculation change; frozen outputs
byte-identical, suite green):

- Ruleset state vocabulary corrected in code and docs: `fide-2026`
  status is now `specified` (was `reserved`) in `RulesetInfo`,
  error messages, and all documents — "specified, implementation
  pending (Phase F26-1)". Strict refusal behavior unchanged
  (`UnsupportedRulesetError`); affected tests updated.
- Requirements matrix now carries per-ruleset states (`2024:
  IMPLEMENTED · 2026: IMPLEMENTATION_PENDING`) so 2024 implementation
  can never be read as 2026 implementation; roadmap matrix scope-noted.
- Integration contract gains the modifiers clause (distinct ids today;
  `/P` + mode flags as additive F26-1 parameters; `OTHER_*` never
  forwarded); README lists all three rulesets with states.
- TPR fraction-rounding and empty-set zero labeled as documented
  interpretations; VIRTUAL-sentinel vs FIDE-dummy terminology note;
  ETT26/192 regime mapping in format variants + inventory + master spec.

## [0.5.1] — 2026-10-03

Documentation reconciliation (no calculation change; suite green):

- Corrected the false "ETT26 does not exist" conclusion: ETT26 exists as
  C.02.03 Annex C (Tournament Type Code Table for TRF field 192).
  TEC-table extraction + Handbook indexed text verified; 192→regime
  mapping documented; TRF-parser/ETT-lookup ownership fixed consumer-side.
- C.02.01/03/04 hierarchy reconciled from current sources (framework vs
  software vs register); C.07 reachability re-checked (hosts still
  unreachable; fallback + date/instrument split retained); MTB26
  descriptor→core-request boundary specified (`OTHER_*` never a FIDE
  criterion; modifiers semantic; order consumer-controlled).
- Stale claims fixed (publication status, ADR-007 premises with status
  note, roadmap phases F26-1/F26-2/team/differential, `reserved` =
  specified-pending-implementation everywhere); TPR interpretation
  labeled derived; VIRTUAL-sentinel vs FIDE-dummy terminology note;
  team rows carry THP-mandatory YES + deferral reason; uncertainty
  register classified blocking/non-blocking (only N-STD blocks its own
  P1 phase; nothing blocks F26-1).

## [0.5.0] — 2026-10-03

Final documentation closure (no calculation change; suite green,
frozen outputs byte-identical):

- MTB26 fully catalogued (`docs/FIDE_MTB26_CATALOG.md`): descriptor
  grammar (`Name[:MP/:GP][/…]`), Tables 1–3, full code table,
  generic `/Cn /Mn /Lx /Kx` machine, `/P /F /R` options, `OTHER_*`
  mechanism; defined-vs-listed-vs-mandatory-vs-optional-vs-consumer
  distinction.
- Approval/test ecosystem closed: TEC Manual v1.24 audited
  (`FIDE_TEC_IMPLEMENTATION_REQUIREMENTS.md`: PTC/RTG, 50k-tournament
  protocol, discrepancy classes, external-engine exemption; ETT26
  recorded as non-existent — instruments are PTC+RTG+TRF),
  C.02.01/03/04 framework (`FIDE_SOFTWARE_CONFORMANCE.md`: what a
  compliant program is; TAPC≠endorsement), TRF26 interchange boundary
  (`FIDE_TRF26_INTEROPERABILITY.md`: 202/212/192/013/240/320/801/802,
  parser-vs-core split), approval path (`FIDE_APPROVAL_PATH.md`:
  conformant vs approved; tie-break TAPC testing starts in the future;
  no "FIDE-approved" claim anywhere).
- Modifiers (`FIDE_TIEBREAK_MODIFIERS.md`), format variants
  (`FIDE_FORMAT_VARIANTS.md`: Swiss/RR/team/KO/rapid + C.04 boundary),
  official examples (`FIDE_OFFICIAL_EXAMPLES.md`: Manual annex + TEC
  chapters + tables + Olympiad-2026 OTHER_ reference + recorded
  negatives), source registry (`FIDE_SOURCE_REGISTRY.md`: 21 sources
  with hashes/URLs/effective dates), complete requirements matrix
  (`FIDE_COMPLETE_REQUIREMENTS_MATRIX.md`: Q-/T-/G-/I-/X-rows +
  acronym↔id↔requirement crosswalk).
- Adversarial closure: Olympiad-2026 bespoke systems recorded as
  OTHER_ differential material; FTM stub recorded; VCL-pending noted.
  Consistency audit automated (no forbidden claims, no dangling refs,
  no TODOs, id crosswalk complete). Verdict: CONDITIONALLY CLOSED
  (see final report) — implementation may proceed without further
  research barring new FIDE revisions.

## [0.4.0] — 2026-10-03

Research mission (no calculation change; all frozen outputs byte-identical,
proven by the suite):

- Complete FIDE tie-break domain specification: `docs/FIDE_TIEBREAK_MASTER_SPEC.md`
  + `FIDE_RULE_INVENTORY.md` (39 normative rules) + `FIDE_CRITERIA_CATALOG.md`
  + `FIDE_RULESET_HISTORY.md` (pre-2023 → Mar-2026) + `FIDE_2026_DIFF.md`
  (verified word-level 2024→2026 delta, D1–D15) + `FIDE_DATA_SEMANTICS.md`
  + `FIDE_CONFORMANCE_PLAN.md` + `SOFTWARE_COMPARISON.md`
  + `ARCHITECTURE_GAP_ANALYSIS.md` + `IMPLEMENTATION_ROADMAP.md`
  (requirements matrix, 1.0 gate, uncertainty register).
- March-2026 C.07 full text retrieved via the official Arbiters' Manual 2026
  (Handbook HTML unreachable); TEC Exercises V01-1, both C.07 Tables of Changes,
  2022 text, C.04 Swiss Basic Rules, Rating/Title Regulations retrieved.
  `fide-2026` moves reserved → SPECIFIED (no engine change).
- Corpus `tests/corpus/fide2026_unplayed.json`: 4 VERIFIED fide-2024 vectors
  from official worked examples (Laxman BH 57/C1 50/SB 37.25, Ex01 BH 51,
  Ex03 BH 64.5, Ex04 BH 74, TEC-Ex06 BH-C1 11.5) + 6 PENDING fide-2026 shells
  (NEW-regime values 55/50/37.25, 49.5, 63, 69).
- Findings: 2026 is a bounded delta (STD/TPN/RTNG, RR-ban note, AOB-FB note,
  first-rating rule, EDE chain names, §15.2 carve-out, §16.4 dummy caps);
  architecture needs no structural change; team systems stay out (TeamMatch
  domain); C.04 pairing quantities belong to pairing-core; B.01 norm-TPR
  must never share code with tiebreak-TPR.

## [0.3.0] — 2026-10-03

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
- Rating family under fide-2024 (`tpr`, `ptp`, `apro`, `appo`,
  §§10.2–10.5) from fully-extracted official §§8.1a/8.1b tables, with
  documented interpretations (half-up fraction rounding, OTB-points PTP
  target, TPR on rounded ARO). Corpus case `FIDE2024-RATINGS-TPR-PTP`
  (VERIFIED: hand derivations + brute-force cross-checks).
- Direct Encounter (§6) as a group-level ranking stage under fide-2024:
  mini-standings (played games only, forfeit exclusion, repeated-meeting
  averages with exact arithmetic), subset reapplication (§6.2), Swiss
  certainty ranking (§6.3). Positional in criteria sequences; scalar
  `direct_encounter` raises `UnsupportedCriterionError` (no per-player
  scalar exists). Corpus cases `FIDE2024-DE-HEADTOHEAD`,
  `FIDE2024-DE-CERTAINTY` (VERIFIED). See ADR-008.
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
