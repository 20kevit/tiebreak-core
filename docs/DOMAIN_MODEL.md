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

## Terminology: VIRTUAL sentinel vs FIDE dummy (not the same thing)

`VIRTUAL_OPPONENT` / `VIRTUAL_KINDS` are legacy input-layer names for
the `-1` "no scheduled opponent" sentinel. They are NOT the FIDE
"virtual opponent" abolished in 2023, and NOT the §16.4 "dummy"
(a calculation fiction: a nominal opponent credited with the
participant's own — capped in 2026 — score). The sentinel marks
missing input; the dummy is produced by the engine. Do not conflate
the three.

## Game kinds (Phase 1, additive)

`GameRecord.kind` (`""` = unspecified) says WHAT happened, from
`GAME_KINDS`: `played`, `pairing_bye` (§16.2.1), `forfeit_win`
(§16.2.2), `forfeit_loss` (§16.2.4), `requested_bye` (§16.2.3/§16.2.5;
post-withdrawal rounds are zero-point requested byes per §16.1.1),
`unplayed` (legacy generic), `absent` (no pairing at all).

- Unspecified normalizes via `normalize_kind()`: `-1` → `unplayed`,
  real opponent → `played`. Old inputs keep exact legacy meaning.
- Legacy calculators ignore `kind`. Future `fide-2026` calculators
  branch on it. Strict path validates vocabulary + kind/opponent
  consistency (explicit `played` needs a real opponent; bye-like kinds
  need `-1`; forfeits allow a scheduled opponent or `-1`).
- Chess-manager 9-type → kind guidance for adapters: `1-0/0-1/1/2` →
  `played`; `+/-` → `forfeit_win`; `-/+` → `forfeit_loss`;
  `bye` → `pairing_bye`; `half-bye/zero-bye` → `requested_bye`;
  missing slot → `absent` (or legacy `-1` unspecified).

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
