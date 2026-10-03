# FIDE conformance plan

## Unit tests — every formula
Cover each calculator incl. zero/edge: BH/C1/C2/M1/M2, SB/SB-C1,
PS/PS-C1, WIN/WON/BPG/BWG/REP, ARO/ARO-C1, AOB, FB, Koya
(threshold boundary at exactly 50%), TPR/PTP/APRO/APPO (table
boundaries p=0/0.5/1, D=0/±400/±735 with tolerance), DE stages.
Status: IMPLEMENTED (`tests/test_calculators.py`,
`test_fide2024.py`, `test_ratings.py`, `test_direct.py`).

## Rule tests — every normative FIDE rule
One test per `FIDE_RULE_INVENTORY.md` row where the rule is
IMPLEMENTED (e.g. R-VURCUT higher-of for SB-C1; R-DE-AVG exact
averages; R-DUMMY24 uncapped). SPECIFIED rows get PENDING corpus
shells instead. Status: IMPLEMENTED for the fide-2024 subset.

## Corpus tests — every official worked example
- TEC Exercises V01-1 (2024-04): BH 13.0 / BH-C1 11.5 fully-played
  vectors (FIDE_SOURCES item 4) + Ex06 VUR case
  (`TEC-EX06-2024-BHC1` VERIFIED; `TEC-EX06-2026-BHC1` PENDING).
- Arbiter Manual 2026 annex: Laxman triple + Ex01/03/04 OLD/NEW
  (`tests/corpus/fide2026_unplayed.json`: 4 VERIFIED fide-2024
  + 6 PENDING fide-2026). Ex02 (no-op cap) and Ex05 (officially
  under-specified) stay docs-only by design.
- Fully-played definition cases (`fide_definitions.json`) remain
  version-agnostic VERIFIED.
Rule: never invent expected values; PENDING shells carry inputs +
official numbers in `notes` until the ruleset executes.

## Differential tests
- Official examples (above) — primary.
- Published standings (chess-results.com TB annotations, Olympiad
  tables, WRBC AROC1 lists) — SECONDARY, useful for custom-descriptor
  parsing and smoke values, never normative.
- Oracles: `@echecs/*@4.1.0` vitest vectors (MIT, runnable),
  Gacrux TieBreakServer RTG-seeded TRF corpora (`-g` + `tiebreakchecker
  -c`). Cross-check only.

## Property tests (recommended next)
Determinism (25× repeat pins exist); permutation stability of
`rank_standings`; exactness (Fraction spot-checks on BH/SB/DE
averages); termination (DE reapplication depth bound = group size);
no-mutation (frozen outputs). Add hypothesis-style round-trip for
classify→adjusted→dummy when fide-2026 lands.

## Regression tests
Every historical bug becomes a test (policy in ARCHITECTURE.md).
Known traps to pin: legacy rounding-before-ranking (frozen),
median fallbacks, `<2 rated opponents` ARO-C1, zero-target PTP
(−800), empty-rating TPR (0.0), last-element cut guard.

## Performance tests
Benchmarks exist (`tests/test_benchmarks.py`: 2000-player 7-round
synthetic). Required before 1.0: 100/500/1000/2000 players,
worst-case recursive DE (long tied chains), worst-case rating
recursion (APRO/APPO over large OTB sets), long criterion
sequences. Budget: keep 2000-player full-sequence under ~1s.
