# Integration: chess-manager consumes tiebreak-core (adapter pattern)

## Adapter ownership

All database access lives in ONE manager-side module (currently
`application/tournament/tiebreak_adapter.py`). The adapter translates
persistence rows into `PlayerTiebreakData` / `GameRecord`:

- `player_id` ← participant id; `rating` ← rating snapshot;
  `points` ← pre-accumulated final score (the core never sums results).
- One `GameRecord` per side present; unplayed/missing-opponent games →
  `opponent_id=-1` with the score from the manager's result table.
- `criteria` order ← tournament configuration; `total_rounds`/context ←
  tournament state; `deterministic_keys` ← `pairing_no or start_number`.

## Recommended call pattern

```python
from tiebreak_core import rank_standings  # or the strict variant

standings = rank_standings(tb_inputs, criteria, current_round,
                           deterministic_keys=keys)
# standings.rules_version records the producing ruleset — store it
# alongside published standings for reproducibility.
```

Keep in the manager: seeding (round 0), withdrawal filtering, rating
reports, prizes, print/export, UI, persistence. The core must never
import manager models.

## Ruleset upgrades

When `fide-2026` lands, adopt it per-tournament (configuration), never
by silent global switch: historical events keep `legacy-0.1.0` results.
Mixed-ruleset displays must label the producing ruleset per row/table.
