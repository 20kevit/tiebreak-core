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

## Phase 2 — fide-2026 calculation engine

- Objective: FIDE-correct calculations under explicit `ruleset="fide-2026"`.
- Scope: Article 16 virtual-opponent arithmetic + cut exception (16.5),
  full ARPO conversion table, Koya round-robin gating, SB/PS/ARO Cut
  variants. Each needs the official article text retrieved in full
  (direct Handbook fetch timed out in this mission — re-retrieve).
- Deliverables: new code paths only, corpus VERIFIED cases from official
  worked examples (TEC exercises), legacy goldens untouched.
- Definition of Done: corpus `fide-2026` cases pass; legacy suite green.

## Phase 3 — Direct Encounter architecture

- Objective: §6 mini-standings with subset reapplication.
- Scope: group-context ranking (`criterion → group → subset →
  recursive calculation` with termination proof), multi-way tie corpus.
- Definition of Done: 3+-player tie corpus green; stub retained under
  legacy only.

## Phase 4 — Rating-based family + remaining FIDE systems

- Objective: ARO-C1, APRO/APPO/PTP/TPR/RTNG, AOB, ForeBH, REP/STD/TPN,
  team systems (if demanded) — each with verified definition or
  documented gap (never fabricated formulas).
- Definition of Done: capability matrix (MASTER_PLAN) all-green or
  explicitly deferred with rationale.

## Phase 5 — Consumer adoption + 1.0 release

- Objective: chess-manager per-tournament ruleset selection,
  pairing-core narrow-contract adoption where needed, 1.0 release.
- Definition of Done: clean-install pins, integration tests, tag.
