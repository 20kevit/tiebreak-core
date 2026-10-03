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

## Finalized consumer contract (closure mission)

- **Core-owned**: per-criterion values, Art 15/16 unplayed semantics,
  DE group stages, rating-family values, exact ordering under an
  explicit list + ruleset, typed errors, frozen ruleset pins, MTB26
  descriptor ids for calculation requests. Full semantics:
  `ARCHITECTURE_GAP_ANALYSIS.md` (§26 rank_standings contract).
- **Manager-owned**: building inputs (EVERY unplayed round categorized
  — uncategorized `-1` is rejected under fide-2024); per-tournament
  criterion order (MTB26 descriptors from TRF 202/212, incl. `OTHER_*`
  for self-defined lists — the core calculates listed FIDE codes and
  must not silently invent `OTHER_*` values); per-tournament ruleset
  pin stored with standings; seeding (round 0); withdrawal filtering;
  FIRST-rating snapshot (2026 §10 note); unrated-handling policy text;
  scoring-table context (TRF 013) for future STD; pairing numbers for
  future TPN; presentation/prizes/persistence/TRF I/O.
- **Input model**: `PlayerTiebreakData` + `GameRecord` + `GAME_KINDS`
  (+ future: Swiss/RR mode flag, scheduled-opp scores, pairing nos).
  TRF mapping table: `FIDE_TRF26_INTEROPERABILITY.md`.
- **Output model**: `StandingsResult` (ordered, criteria, rules_version).
  Equal values → deterministic-key order (then lots/consumer policy).
- **Error handling**: strict raises typed errors (manager maps to
  arbiter-facing messages / 4xx); legacy never raises (frozen).
- **Version compatibility**: additive ids only; `fide-2026` opt-in per
  tournament; mixed-ruleset displays labeled per row/table.
- Chess-manager code itself is NOT modified by this repository
  (external state; concurrent work respected).
