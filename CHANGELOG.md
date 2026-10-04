# Changelog

All notable changes to `tiebreak-core` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Ruleset versions (e.g. `legacy-0.1.0`, `fide-2026`) are independent of
package versions — see `docs/VERSIONING.md`. A frozen ruleset's outputs
never change across package releases.

## [1.2.0] — 2026-10-04

Correctness release (additive API + one documented correction).

Correction F4 (P0): the Direct/Extended Direct Encounter mini-tables
(`fide2024._mini_table`, `fide2026._mini_table`,
`team._mini_scores`) credited only the first-iterated side of each
pair, dropping the other side's games whenever group order put it
second — e.g. A-beats-B ordered `[B, A]` scored `{A: 0, B: 0}`
instead of `{A: 1, B: 0}`, and a mutual draw scored `{first: 0.5,
other: 0}` instead of `0.5–0.5`. Same logical tournament in
different input order could therefore produce different DE tiers
(determinism breach; contradicts §6.1, §6.1.2 and the modules' own
docstrings). Pair iteration now credits each side's own games to
itself. Before/after verified: the entire suite (incl. all official
corpus values and differential fixtures) passes identically with
old and new tables — no pinned or official value changes; only
previously order-dependent (non-contractual) outcomes move, always
toward the documented algorithm. Recorded as a pre-publication
correction (no PyPI release and no adopted consumer of 1.x outputs
exists yet); post-publication the freeze is absolute — see
`docs/VERSIONING.md`.

Also additive (backwards-compatible): top-level exports for
`calculate_descriptor_strict`, `rank_descriptors_strict`,
`calculate_team_strict`, `rank_teams_strict`, `canonical_team_id`;
player/team id as the final ranking tiebreak so colliding caller
keys cannot leak input order; executable `examples/` A–G with CI
gate (`tests/test_examples.py`); order-invariance regression tests
(`tests/test_de_order_invariance.py`); rewritten README;
`docs/DEVELOPMENT.md` + `docs/RELEASING.md`; packaging metadata
(Production/Stable, keywords, Homepage); CI packaging validation
(sdist + `twine check` + wheel/sdist clean-install smoke).

Suite: 652 passed + benchmarks, 66 documented differential skips.
No FIDE approval/acceptance claimed.

## [1.1.0] — 2026-10-04

Additive minor: generic MTB26 modifier engine, team domain, Article-16
policy and scoring-scheme models. No published ruleset output changes
(proven by the untouched frozen suites + named-equivalence tests).

Added:

- `tiebreak_core.modifiers`: MTB26 descriptor grammar
  (`Name[:MP|:GP][/Cn][/Mn][/L±n][/Kx][/P][/F][/R]`) with typed
  `InvalidDescriptorError` rejection of FIDE-undefined combos;
  generic /Cn /Mn calculators (BH/SB/ARO/FB families, PS/Cn as
  round-exclusion generalising §14.1.1.c); `/P` → forfeit inclusion,
  `/L±n` → Koya half-point limits, `/R` → terminal reversal in
  `rank_descriptors`. n=1/2 delegate to the named ids
  (equivalence-pinned); `fide-2024` keeps named ids only.
- `tiebreak_core.team`: team domain beside (not inside) `GameRecord` —
  `TeamMatch`/`TeamRecord`/`TeamFormat`; MP/GP (§11), BC/TBR/BBE
  (§12), MPvGP/ESB×4/EDE+chains/SSSC (§13), ESB-C1/C2 (§14.1.2),
  Table-2 reuse on :MP/:GP refs (§13 blanket rule), staged
  `rank_team_standings` (BC ascending, TBR/BBE reapplication keys,
  pair-only §13.3.2 chains). Tests are definition-derived hand
  calculations (no official team example retrieved — never labelled
  official); unretrieved edges are documented PROJECT_DERIVED
  interpretations.
- `tiebreak_core.article16`: `Article16Policy` value object +
  `resolve_policy` (§16.6 overrides recorded/validated; engine
  defaults unchanged).
- `tiebreak_core.scoring`: `ScoringScheme` model + explicit-input
  rule for exotic tables.
- Strict wrappers: `calculate_descriptor_strict`,
  `rank_descriptors_strict`, `calculate_team_strict`,
  `rank_teams_strict`.

Suite: 639 passed (503 pre-existing untouched + 136 new), 66 skipped.
Benchmarks added: descriptor-heavy ranking (n=500) + team ranking
(n=200). No FIDE approval/acceptance claimed.

## [1.0.0] — 2026-10-04

First stable release: complete individual-tournament tie-break core
for `fide-2024` (frozen era semantics) and `fide-2026` (current
C.07). Public API frozen at this contract (additive extensions only
henceforth; output-changing corrections to published rulesets
require new ruleset ids per `docs/VERSIONING.md`).

Since 0.9.0: AOB/FB exact ranking, Koya §14.5 limits, FB/ARO median
combos, fide-2024 shared-context performance (100×, identical
outputs), echecs differential harness (10 fixtures), 3 official TEC
corpus cases, source registry, versioning-policy resolution. Suite:
503 passed. No FIDE approval/acceptance claimed (see
`docs/FIDE_APPROVAL_PATH.md`).

## [0.9.0] — 2026-10-03

Correctness remediation (independent audit F1/F2/F3). API
backwards-compatible; three calculation corrections change affected
values — pre-1.0 rulesets, no consumer adoption yet (integration
contract still future-tense), so fixed in place with explicit
before/after notice rather than new ruleset ids:

- F1 (P0): SB-C1/SB-C2 cut the product of the lowest-SCORED
  opponent (§14.1.1.d + TEC worked rule), not the least product.
  E.g. win-vs-2.0 (2.0) + draw-vs-3.0 (1.5): cut is now 2.0 (was
  1.5). Official TEC Stephan SB-C1 5.75 (was 7.25), Maria 4.25
  (was 5.75) — added as corpus `TEC-SB-C1-STEPHAN-MARIA`. Base SB
  unchanged. Affects fide-2024 + fide-2026. Hand-derived P2
  SWISS5 SB-C1 corrected 2.75 → 2.25 (lowest basis R3 0.5).
- F2 (P1): requested FULL-point byes are 16.2.1 non-VUR (§16.1.1
  defines requested byes as half/zero-point only). Affects VUR-cut
  preference + REP for such rounds; all other categories unchanged.
  Affects fide-2024 + fide-2026 (shared classifier).
- F3 (P1): AOB returns the exact mean (§8.2 states no rounding);
  ranking sorts on the exact value (was 1dp-rounded). E.g.
  SWISS5 P1 AOB 12.7 → 12.666666666666666 (38/3). `aob_fb`
  intentionally unchanged (stability test added).

## [0.8.0] — 2026-10-03

Phase F26-2: close the specified individual-Swiss surface under
`fide-2026` (additive new criteria; frozen outputs byte-identical):

- STD (§7.7, Q-STD): new `std` criterion + optional
  `GameRecord.opponent_score` input (backwards-compatible: appended
  optional field; legacy/fide-2024 ignore it). Played rounds compare
  against the scheduled opponent's round score (explicit value, else
  standard 1-½-0 complement when `draw_points == 0.5`); unplayed
  rounds compare against the draw value; RR-mode/`/P` forfeits count
  as regular games. Non-standard draw values without explicit scores
  raise `InvalidPlayerDataError` (organizer contract; U6 now blocks
  exotic scoring tables only).
- Cut combos: `sonneborn_berger_cut2` (SB-C2 = reapplied C1-cut per
  §16.5.2, documented interpretation), `aro_cut2` (drop two lowest,
  keep-≥1 guard mirroring BH-C2), `fore_buchholz_cut1/cut2`,
  `aob_fb` (AOB over Fore Buchholz, D8). All hand-computed +
  chain-monotonicity property tests. PS-C2 deliberately NOT built
  (no FIDE semantics exist — PS-C1 is round-exclusion).
- Robustness: dangling over-the-board opponent references now raise
  `InvalidPlayerDataError` under fide-2024/fide-2026 instead of a bare
  `KeyError` (valid-input outputs unaffected; the crash site surfaced
  during fixture work).
- Matrix/modifiers/MTB26/roadmap states updated to the exact
  remaining scope (generic /Cn /Mn machine, Koya limits, team,
  16.6, exotic STD).

## [0.7.0] — 2026-10-03

Phase F26-1: `fide-2026` implemented (Swiss scope + RR mode; suite
197 passed, 0 skipped; frozen outputs byte-identical):

- New engine `tiebreak_core.fide2026` (ruleset `fide-2026`,
  status implemented): the full fide-2024 Swiss core plus the March-2026
  §16.4 dummy caps — 16.4.1 scheduled-opponent cap for forfeit rounds,
  16.4.2 draw-points × rounds cap otherwise. All five encoded official
  NEW-regime expectations reproduce the Manual's printed numbers
  (BH 57→55, 51→49.5, 64.5→63, 74→69, BH-C1 50/11.5, SB 37.25).
- Explicit `mode="swiss"|"round_robin"` regime flag implementing the
  §15.2 round-robin forfeit carve-out (D12); `draw_points=0.5`
  (§16.4.2 draw value); `forfeits_as_played=False` (MTB26 `/P`
  opt-in for BH/SB/FB/Koya/DE; Type-B and rating sets unaffected);
  terminal ranking stages `tpn` (§7.8, ascending, needs
  `pairing_numbers`) and `rtng` (§10.6, descending). Strict surface
  dispatches all of them; non-2026 rulesets reject them with typed
  errors (never silent behavior).
- Corpus: all 9 PENDING shells → VERIFIED (5 unplayed NEW-regime +
  ART16 taxonomy + DE minitable + MEDIAN2 + SB-C1, the latter upgraded
  SECONDARY→PRIMARY on the retrieved article text). EX04 Amit stub
  completed (R1 forfeit loss + R2–R10 trailing zero-byes, mirroring
  the EX01 Leo pattern) with an explicit input note; residual
  exclusion-vs-bye ambiguity recorded as roadmap U11.
- Tests: new F26-1 suite (caps, Swiss 2024≡2026 parity on
  fully-played events, 2026≤2024 monotonicity on 30 random Swiss
  events, RR carve-out, terminals, /P scope, properties:
  determinism, permutation invariance, no-mutation, DE termination
  incl. a 30-player all-draw group, adversarial all-tied field).
  `tests/test_benchmarks.py` gains a 2000-player fide-2026 ranking
  (0.22s via once-per-standings shared context; the naive
  per-(player, criterion) rebuild was quadratic and timed out).
- Docs: requirements matrix per-ruleset states flipped to
  2026-IMPLEMENTED (exact scope retained: STD, /C2-/Cn-/Mn-combos,
  Koya limits, team, 16.6 still out); modifiers/MTB26/adapter/API/
  roadmap/PERFORMANCE updated; `fide-2024` outputs unchanged.
- FIDE-status honesty: specification implemented + official-example
  verification; no FIDE approval/acceptance claimed.

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
