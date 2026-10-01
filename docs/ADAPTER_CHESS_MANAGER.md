# Adapter contract: CHESS-MANAGER → TIEBREAK-CORE

> Principle: tiebreak-core never queries chess-manager's database.
> chess-manager builds inputs, calls the core, and renders outputs.

## Source fields (chess-manager owns persistence)

| Core input | Source |
|---|---|
| `player_id` | `TournamentParticipantModel.id` |
| `rating` | `participant.rating_snapshot or 0` |
| `points` | `participant.points or 0.0` (pre-accumulated by round lifecycle; core never sums) |
| `game.opponent_id` | opposing `PairingModel.white/black_participant_id`, or `-1` (see below) |
| `game.score` | 9-type result table (§ result mapping) |
| `game.color` | `"white"` / `"black"` (side the player sat) |
| `game.round_number` | `RoundModel.round_number` via `pairing.round_id` |
| `game.opponent_rating` | opponent's `rating_snapshot or 0` (informational) |
| `criteria` order | `json.loads(tournament.tiebreak_rules or "[]")` |
| `total_rounds` (Koya) | `tournament.current_round` (legacy quirk, preserved) |
| `deterministic_keys` | `participant.pairing_no or start_number or 999` |

## Result mapping (9 types → score + virtual flag)

```
1-0:(1.0,0.0)  0-1:(0.0,1.0)  1/2:(0.5,0.5)  +/-:(1.0,0.0)
-/+:(0.0,1.0)  +/+:(0.0,0.0)  bye:(1.0,–)  half-bye:(0.5,–)  zero-bye:(0.0,–)
```

A `GameRecord` is emitted per side present in the pairing. A side becomes
`opponent_id=-1` when: the result is unplayed
(`+/- -/+ +/+ bye half-bye zero-bye`) OR the opposing slot is empty/missing.
Played results with both sides present use the real opponent id.

## Virtual opponent behavior (legacy, preserved)

Calculators substitute `max(0.0, player.points - game.score)` for `-1`
games (Buchholz family, SB, Koya). ARO substitutes the player's own rating.
See KNOWN_LIMITATIONS.md (FIDE Art.16 NOT implemented in v0.1.0).

## Ownership

- Points accumulation → chess-manager round lifecycle (incremental +
  full-rebuild). Core assumes `points` is final.
- Rounding → core (legacy: BH 1dp, SB 2dp, ARO/ARPO int). Callers display
  values as returned; no re-rounding before ranking.
- Ranking values+order → core (`rank_standings`) for active standings;
  initial seeding (`current_round == 0`, rating DESC + start_number ASC) →
  chess-manager (NOT in core).
- Tournament configuration (`tiebreak_rules` JSON, `total_rounds`,
  `current_round`) → chess-manager. `DEFAULT_CRITERIA` in the core is a
  fallback reference only.
- Withdrawal filtering (`status != active and points == 0` skipped) →
  chess-manager, before calling the core.
- Presentation (Persian names, tables, print) → chess-manager templates.

## Minimal call

```python
from tiebreak_core import calculate_all, rank_standings
# build tb_data: {pid: PlayerTiebreakData} per § mapping, then:
values = calculate_all(tb_data[pid], tb_data, criteria, tournament.current_round)
standings = rank_standings(tb_data, criteria, tournament.current_round,
                           deterministic_keys={pid: (p.pairing_no or p.start_number or 999)})
```
