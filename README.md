# tiebreak-core

Standalone chess tie-break calculation library — behavior-preserving
extraction from `chess-manager` `domain/tiebreak/`.

- No Flask, no SQLAlchemy, no persistence, no network, zero runtime deps.
- Deterministic: same input + same rules version → same output.
- Rules version: `legacy-0.1.0` (see `src/tiebreak_core/rules.py`).
- Reference for future work: FIDE Handbook C.07 (see `docs/TIEBREAK_RULES.md`).
- Relationship: `chess-manager → tiebreak-core ← (future) pairing-core`.
  `pairing-core` does NOT depend on `tiebreak-core` (see `docs/COMPATIBILITY.md`).

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

## What it is / is NOT

- IS: pure tie-break calculators + explicit ranking comparator + versioned rules model.
- IS NOT: a tournament manager, persistence, HTTP service, Elo engine,
  pairing engine, TRF/Coronate I/O, or UI formatting (Persian names live in
  `tiebreak_core.display`, outside the calculation path).

## Layout

- `src/tiebreak_core/` — `models`, `calculators`, `registry`, `ranking`,
  `display` (optional), `rules`
- `tests/` — ported units + golden/conformance (`data_goldens.json`) + ranking + determinism
- `docs/` — standalone + integration documentation

## Docs

Start with `docs/ARCHITECTURE.md`, then `docs/API.md` (standalone use) and
`docs/ADAPTER_CHESS_MANAGER.md` (chess-manager integration). Known
divergences from FIDE are in `docs/KNOWN_LIMITATIONS.md` — they are
intentionally NOT fixed in v0.1.0.
