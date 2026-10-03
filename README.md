# tiebreak-core

Standalone chess tie-break calculation library: correct, deterministic,
well-specified calculation of chess tournament tie-break criteria.
Zero runtime dependencies, stdlib only, Python `>=3.10`, MIT.

- Deterministic: same input + same ruleset → same output.
- Rulesets are explicit and inspectable: `legacy-0.1.0` (frozen
  behavior-preserving extraction), `fide-2024` (implemented, frozen),
  and specified-but-unimplemented `fide-2026` (implementation pending,
  Phase F26-1 — see `src/tiebreak_core/rules.py`, `docs/VERSIONING.md`,
  `docs/FIDE_2026_DIFF.md`).
- Reference: FIDE Handbook C.07 (see `docs/TIEBREAK_RULES.md`,
  `docs/FIDE_SOURCES.md`).
- Relationship: `chess-manager → tiebreak-core ← pairing-core callers`
  (narrow scalar/vector data only — `pairing-core` does NOT depend on
  `tiebreak-core`; see `docs/COMPATIBILITY.md`).

## Install

```bash
pip install -e .
```

## Use (standalone — no chess-manager needed)

```python
from tiebreak_core import (
    PlayerTiebreakData, GameRecord, calculate_all, rank_standings,
)

players = {
    1: PlayerTiebreakData(1, 2000, 2.5, [
        GameRecord(2, 1900, 1.0, "white", 1),
        GameRecord(3, 1800, 0.5, "white", 2),
    ]),
    2: PlayerTiebreakData(2, 1900, 0.5, []),
    3: PlayerTiebreakData(3, 1800, 1.0, []),
}
criteria = ["buchholz_cut1", "buchholz", "sonneborn_berger", "progressive"]

# Values only (composable, no ranking):
values = calculate_all(players[1], players, criteria, total_rounds=5)

# Values + explicit-policy ranking (no seeding inside the core):
standings = rank_standings(players, criteria, total_rounds=5,
                           deterministic_keys={1: 1, 2: 2, 3: 3})
for pr in standings.players:
    print(pr.rank, pr.player_id, pr.points, pr.values)
```

Strict fail-fast variant (same values, typed errors, explicit ruleset):

```python
from tiebreak_core import calculate_all_strict
values = calculate_all_strict(players[1], players, criteria, 5,
                              ruleset="legacy-0.1.0")
```

## What it is / is NOT

- IS: pure tie-break calculators + explicit ranking comparator +
  inspectable ruleset model + strict validation boundary.
- IS NOT: a tournament manager, persistence, HTTP service, Elo engine,
  pairing engine, TRF/Coronate I/O, or UI formatting (Persian names live in
  `tiebreak_core.display`, outside the calculation path).

## Layout

- `src/tiebreak_core/` — `models`, `calculators`, `ranking`, `strict`,
  `errors`, `registry`, `display` (optional), `rules`
- `tests/` — units + golden/conformance + FIDE corpus (`tests/corpus/`)
  + ranking + strict + determinism + benchmarks
- `docs/` — architecture, API, ADRs (`docs/adr/`), rulesets, roadmap,
  master plan, integration, conformance methodology

## Docs

Start with `docs/ARCHITECTURE.md`, then `docs/API.md` (standalone use),
`docs/INTEGRATION_CHESS_MANAGER.md` / `docs/INTEGRATION_PAIRING_CORE.md`
(consumer contracts), and `docs/ROADMAP.md` + `docs/MASTER_PLAN.md`
(where the project is going). Known divergences from FIDE are in
`docs/KNOWN_LIMITATIONS.md`. Releases: `CHANGELOG.md`.
