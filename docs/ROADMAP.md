# Roadmap

Large coherent phases only. Each phase ships code + tests + docs +
CHANGELOG entry; `main` stays green throughout.

## Phase 1 — Unplayed-game taxonomy (input foundation for fide-2026)

- Objective: represent what `-1` conflates today.
- Scope: new explicit game-kind fields (pairing-allocated bye,
  full-point bye, forfeit win/loss, requested half/zero bye, withdrawal
  rounds, missing opponent), validated on the strict path; legacy `-1`
  inputs keep working via a documented default-kind mapping.
- Deliverables: domain model extension, validation, unit tests,
  corpus PENDING→VERIFIED shells for Art.16 categories (no Art.16
  arithmetic yet).
- Definition of Done: taxonomy documented in DOMAIN_MODEL, old inputs
  byte-compatible, new fields exercised by tests.

## Phase 2 — fide-2026 calculation engine (SPECIFIED 2026-10-03, build: Phase F26-1)

- Objective: FIDE-correct calculations under explicit `ruleset="fide-2026"`.
- Scope (all verified this mission — no further research needed):
  §16.4.1/16.4.2 dummy caps (core), §15.2 RR forfeit carve-out
  (+ explicit Swiss/RR mode input), STD (§7.7, needs scheduled-opp
  scores), TPN/RTNG terminal keys, Art-8 RR-ban note, AOB-FB variant,
  first-rating contract. Full delta: `docs/FIDE_2026_DIFF.md` (D1–D15).
- Deliverables: new code paths only; activate the 6 PENDING shells in
  `tests/corpus/fide2026_unplayed.json`; legacy + fide-2024 goldens untouched.
- Definition of Done: corpus `fide-2026` cases pass; full suite green.
  Build order + 1.0 gate: `docs/IMPLEMENTATION_ROADMAP.md`.

## Phase 3 — Direct Encounter architecture

DONE (2026-10-03, under fide-2024): §6 mini-standings with subset
reapplication (§6.2) and Swiss conditional ranking (§6.3) as a
group-level ranking stage; forfeit exclusion (§6.1.1, Swiss scope);
repeated-meeting averaging (§6.1.2, exact arithmetic). See ADR-008,
`tests/test_direct.py`, corpus `fide2024_direct.json`. Team EDE and
round-robin forfeit inclusion remain future work.

## Phase 4 — Rating-based family + remaining FIDE systems

DONE (2026-10-03, under fide-2024): TPR/PTP/APRO/APPO (§§10.2–10.5)
from fully-extracted official §§8.1a/8.1b tables, with documented
interpretations. See `tests/test_ratings.py`, corpus
`fide2024_ratings.json`. Remaining: team systems (deferred — no team
consumer; needs MP/GP domain objects) and Koya RR-gating policy
(threshold already on maximum-possible; scope decision is caller-side).

## Phase 5 — Consumer adoption + 1.0 release

- Objective: chess-manager per-tournament ruleset selection,
  pairing-core narrow-contract adoption where needed, 1.0 release.
- Definition of Done: clean-install pins, integration tests, tag.
