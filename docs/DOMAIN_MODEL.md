# Domain model

## Inputs (caller-built, core never fetches)

```python
GameRecord(opponent_id: int,   # real id, -1 = virtual (unplayed/missing), see below
           opponent_rating: int,  # informational; ARO reads ratings from all_players
           score: float,           # 1.0 / 0.5 / 0.0  (from the 9-type result table)
           color: str,            # "white" | "black"
           round_number: int)
PlayerTiebreakData(player_id: int, rating: int, points: float,
                   games: list[GameRecord])
```

- `points` is PRE-ACCUMULATED final score. The core never sums results.
- `rating` is the tournament snapshot (used only for ARO/ARPO paths).
- `opponent_id == -1` (VIRTUAL_OPPONENT) marks unplayed/missing-opponent
  games. Calculators substitute `max(0.0, player.points - game.score)`.
  This is legacy behavior (see KNOWN_LIMITATIONS.md), preserved verbatim.
- IDs are plain `int` in v0.1.0 (chess-manager compatible). No generics.

## Outputs (immutable)

```python
PlayerResult(player_id, points, values: {criterion: float}, rank)
StandingsResult(players: (PlayerResult, ...) ordered, criteria, rules_version)
```

Rounding is part of the CALCULATION (legacy): Buchholz family 1dp,
Sonneborn-Berger 2dp, ARO/ARPO integer. Ranking sorts the ROUNDED values.

## Criteria identifiers (stable)

`buchholz buchholz_cut1 buchholz_cut2 median_buchholz median_buchholz_2
sonneborn_berger progressive wins wins_black games_black aro koya
buchholz_sum arpo direct_encounter`

Unknown identifiers → `0.0`. `direct_encounter` at standings level → `0.0`
(stub, see KNOWN_LIMITATIONS). `koya` needs `total_rounds` (threshold
`total_rounds / 2`; `0` → `0.0`).
