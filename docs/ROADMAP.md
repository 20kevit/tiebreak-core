# Roadmap (actionable; history preserved below)

Large coherent phases only. Each phase ships code + tests + docs +
CHANGELOG entry; `main` stays green throughout. Normative source for
priorities/statuses: `docs/FIDE_COMPLETE_REQUIREMENTS_MATRIX.md`.

## F26-1 — fide-2026 foundation (DONE in 0.7.0)

- Objective: FIDE-correct Swiss calculations under explicit
  `ruleset="fide-2026"`; `fide-2024` outputs byte-identical.
- Delivered: §16.4.1/16.4.2 dummy caps; explicit Swiss/RR mode input
  (RR mode implements the §15.2 2026 carve-out); TPN + RTNG terminal
  keys; `/P` forfeit-inclusion flag; first-rating contract wording.
  All 9 PENDING corpus shells → VERIFIED (5 unplayed NEW-regime +
  ART16 taxonomy + DE minitable + MEDIAN2 + SB-C1); property tests
  (determinism, permutation invariance, no-mutation, DE termination,
  2026≤2024 monotonicity); 2000-player fide-2026 bench 0.22s.
- Follow-up: F26-2 (STD + remaining 2026 deltas) is NEXT.

## F26-2 — STD + remaining 2026 deltas (DONE in 0.8.0)

- Delivered: STD (§7.7, standard scoring via explicit `opponent_score`
  or 1-½-0 complement; exotic tables still blocked, U6); AOB-FB
  variant id (`aob_fb`); SB-C2/ARO-C2/FB-C1/FB-C2 combos;
  dangling-opponent typed errors (fide-2024 + fide-2026; crash
  site found by differential fixture work).
- Declined with reasons (not deferred silently): PS-C2 (no FIDE
  semantics — PS-C1 is round-exclusion, not element-cut), generic
  /Cn /Mn machine, Koya limits §14.5 (still SPECIFIED/DEFERRED),
  Art-8 RR-ban enforcement (documented-not-enforced by design).
- NEXT: differential validation + performance + conformance prep;
  consumer per-tournament `fide-2026` opt-in; 1.0 gate per
  IMPLEMENTATION_ROADMAP.

## Team-domain future (on demand — no team consumer today)

- Objective: TeamMatch domain beside (not inside) the core.
- Scope: match/MP/GP/board-vector records; §§11–13 codes;
  §13.3.2 chains; SSSC normaliser; team EDE; team DE/P.
- Definition of Done: deferred until a consumer requires it;
  must NOT stretch `GameRecord` (gap analysis).

## Differential validation + performance + conformance prep

- Objective: PTC-style differential harness (echecsjs/Gacrux oracles,
  RTG-seeded generation), perf budgets (100→2000 players, recursive
  DE, rating recursion, long sequences), consumer per-tournament
  `fide-2026` opt-in, 1.0 gate per roadmap.
- Definition of Done: 1.0 definition met
  (`IMPLEMENTATION_ROADMAP.md`).

## History (completed phases — do not re-plan)

- Phase 1 (taxonomy), Phase 3 (DE stage), Phase 4 (rating family):
  DONE under fide-2024 (see git history + matrix).
- 0.4.0 research mission, 0.5.0 documentation closure: DONE.
