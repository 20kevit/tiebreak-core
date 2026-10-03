# Architecture gap analysis (current vs required)

Verdict: the current architecture supports everything in the
individual-Swiss domain (2024 + specified 2026) **without structural
change**. Required additions are new code paths + two narrow input
extensions, never a redesign. Team systems need a separate domain, not
a core change.

## What already holds

- **Ruleset dispatch** (`rules.py` + strict `ruleset=`): frozen
  `legacy-0.1.0` + implemented `fide-2024` + reserved `fide-2026` (reserved = specified, implementation pending Phase F26-1).
  D13 (dummy caps) and D12 (RR forfeits) fit as new `fide-2026` paths.
- **Game-kind taxonomy** (ADR-006): all Art-16 categories
  expressible; `classify()` positional early/late split verified
  against Ex06 + Manual examples.
- **DE as ranking stage** (ADR-008): §6 mini-standings +
  §6.2 reapplication + §6.3 certainty; positional in criterion
  sequences — this answers §10 of the mission (a general ranking
  engine already exists: scalar calculators + group stages composed by
  `rank_standings[_strict]` over an explicit ordered list, Art 4.2
  subgroups included).
- **Missing-data model** (ADR-004 + DATA_SEMANTICS): typed errors,
  no `missing == 0`.
- **Registry + strict/legacy split** (ADR-002/005): new ids are
  additive; frozen outputs untouched.
- **Determinism/perf**: single-lookup ranking, 2000-player bench.

## Gaps (all bounded)

1. **`fide-2026` engine** — new paths for D13 caps (needs scheduled
   opponent's §16.3 adjustment incl. post-encounter rounds — data
   present in-engine), D12 RR forfeit scope (needs a Swiss/RR mode
   flag: Art 15 vs Art 16 are different regimes, so the mode must be
   explicit input, defaulting Swiss), D5 STD (needs scheduled-opp
   round scores — model gap), D6/D10 TPN/RTNG (terminal keys; TPN
   needs pairing numbers), D7 RR-ban (document; optional warn).
2. **Rating snapshot contract** — document that `rating` = first list
   (D9); no code change.
3. **AOB-FB variant** (D8) — new id if ever requested, not a change.
4. **Koya Limit machinery** (§14.5 ±½) — small parametric extension,
   DEFERRED (no consumer).
5. **Team domain** — separate record type + module/package; explicitly
   not a `GameRecord` extension.
6. **Compound/recursive open points** — EDE chains, SSSC normaliser
   edge cases: team-module concerns; individual side is complete.

## Ownership (mission §18)

- **tiebreak-core**: all individual C.07 calculations, Art 15/16
  semantics, DE/EDE-algorithm shape, rating-family values, exact
  ranking composition, ruleset pins, corpus.
- **pairing-core**: C.04 §§1.7–1.8 opposition evaluation + bracket
  order (current scores, self-game fiction, acceleration exclusion) —
  different inputs, different time (mid-tournament), same names.
  Keep namespaces distinct; never share code.
- **chess-manager**: persistence, registration, seeding (round 0),
  withdrawal filtering, criterion-list selection per tournament,
  unrated-handling policy text, presentation, prizes, TRF I/O.
  Adapter contract: `docs/INTEGRATION_CHESS_MANAGER.md` (+ §26/27
  below).
- **No shared tournament-core**: reaffirmed — composition in
  managers, plain data across boundaries. A team module, if built,
  lives beside (not inside) the core until a second consumer proves
  duplication.

## `rank_standings` contract (§26)

Signature: `rank_standings(players: {id: PlayerTiebreakData},
criteria: [str], total_rounds=0, deterministic_keys={id: key})
→ StandingsResult(players ordered, criteria, rules_version)`.
Ordering: `(-points, [-values[c] for c in criteria],
deterministic_key)`; equal values share no auto-split (DE stages
reorder groups where applicable under fide-2024; otherwise order is
stable by deterministic key, then lots/consumer policy).
`strict` variant validates everything and stamps the requested
ruleset; legacy stamps `legacy-0.1.0`. Backward policy: ordering of
frozen rulesets never changes; new rulesets are new ids.

## Chess-manager adapter contract (§27)

Core owns: values, ordering, ruleset semantics, error taxonomy.
Manager owns: building inputs (incl. categorising every unplayed
round — uncategorized `-1` is rejected under fide-2024), per-tournament
criterion order + ruleset pin (stored alongside standings), seeding,
filtering, ratings snapshot = first list, presentation. Error
behavior: strict raises typed errors (manager maps to 4xx/arbiter
messages); legacy never raises. Compatibility: additive ids only;
`fide-2026` per-tournament opt-in, never global switch.
