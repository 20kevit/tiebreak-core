# API (standalone use)

```python
from tiebreak_core import (
    GameRecord, PlayerTiebreakData,          # inputs
    calculate, calculate_all,                # values (no ranking)
    rank_standings, order_ids, sort_key,     # ordering (no calculation inside order_ids)
    TIEBREAK_IDS, DEFAULT_CRITERIA,          # identifiers
    CALCULATION_RULES_VERSION, is_supported, # versioning
)
from tiebreak_core.display import TIEBREAK_NAMES_FA  # optional, display only
```

## calculate / calculate_all

```python
calculate(player, all_players, "buchholz") -> float
calculate(player, all_players, "koya", total_rounds=5) -> float
calculate_all(player, all_players, ["buchholz", "sonneborn_berger"], total_rounds=5) -> dict
```

Pure, deterministic, no ranking. Use when displaying one player's row,
debugging, or feeding a custom ranking policy.

## rank_standings / order_ids / sort_key

```python
rank_standings(players: {id: PlayerTiebreakData}, criteria: [str],
               total_rounds=0, deterministic_keys={id: key}) -> StandingsResult
order_ids(points: {id: float}, values: {id: {crit: float}}, criteria,
          deterministic_keys) -> [id]   # no recalculation
sort_key(points, values, criteria, deterministic_key) -> tuple
```

Key: `(-points, [-values[c] for c in criteria], deterministic_key)`.
Seeding is NOT included — implement `current_round == 0` branches in the
caller (see ADAPTER_CHESS_MANAGER.md).

## Versioning

`StandingsResult.rules_version == "legacy-0.1.0"`.
`is_supported("legacy-0.1.0") is True`. Future rulesets arrive as NEW
version strings; historical reproducibility is guaranteed by pinning the
version with stored results.

## Adding a new tie-break

1. Add pure function `(player, all_players) -> float` in `calculators.py`.
2. Register id in `TIEBREAK_REGISTRY` + `registry.TIEBREAK_IDS`.
3. Add FIDE ref in `registry.TIEBREAK_FIDE_REF` (or mark non-FIDE).
4. Add optional Persian name ONLY in `display.py`.
5. Add unit + golden cases. If semantics differ from legacy, gate behind a
   NEW rules version — never change legacy outputs.
6. Verify: `pytest`, plus old-vs-new comparison if replacing a legacy id.
