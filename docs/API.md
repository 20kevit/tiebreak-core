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

## Generic modifiers (1.1.0, fide-2026)

```python
from tiebreak_core import (
    parse_descriptor, canonical_id,           # MTB26 grammar -> ModifierSpec
    calculate_descriptor, rank_descriptors,   # individual scope
    InvalidDescriptorError,
)
calculate_descriptor(player, players, "BH/C3", total_rounds=9) -> float
rank_descriptors(players, ["BH/C1", "SB/C1", "DE", "TPN/R"], total_rounds=9,
                 pairing_numbers={...}) -> StandingsResult
```

`/P` enables forfeit inclusion, `/L±n` sets the Koya limit in
half-points, `/R` reverses terminal direction. n=1/2 delegate to the
named ids (equivalence-pinned); FIDE-undefined combos raise
`InvalidDescriptorError`. Strict wrappers:
`calculate_descriptor_strict` / `rank_descriptors_strict`.

## Team domain (1.1.0, C.07 §§11–13)

```python
from tiebreak_core import (
    TeamMatch, TeamRecord, TeamFormat,         # inputs
    calculate_team, rank_team_standings,      # team scope
    validate_team, validate_teams,
)
teams = {1: TeamRecord(1, mp=5.0, gp=9.5, matches=[...],
                       board_points=(3.5, 2.5, 2.0, 1.5))}
rank_team_standings(teams, ["EMMSB", "EDE", "BC"], total_rounds=3,
                    fmt=TeamFormat()) -> TeamStandingsResult
```

Primary MP/GP orders first (default MP, the FIDE default); BC splits
ascending (lower wins); TBR/BBE split by reapplication keys; EDE and
§13.3.2 chains are group stages. Strict wrappers:
`calculate_team_strict` / `rank_teams_strict`.

## Policy / scoring models (1.1.0)

```python
from tiebreak_core import (
    Article16Policy, resolve_policy,          # §16.6 overrides
    ScoringScheme, STANDARD,                  # point tables
)
resolve_policy("fide-2026", mode="round_robin") -> Article16Policy
```

Policies record validated §16.6 overrides (engine defaults unchanged);
exotic scoring tables cross the boundary as explicit per-round inputs.

## Strict path (additive, Phase 0)

```python
from tiebreak_core import (
    calculate_strict, calculate_all_strict,
    rank_standings_strict, order_ids_strict,
    UnknownCriterionError, UnsupportedRulesetError,
    InvalidGameRecordError, InvalidPlayerDataError, RegistryError,
    frozen_registry, register_criterion, is_known,
)
```

Same values/order as legacy for valid inputs under
`ruleset="legacy-0.1.0"` (delegation, proven by
`tests/test_strict.py`). Under `ruleset="fide-2024"` the FIDE-2024
engine computes independently (see `docs/TIEBREAK_RULES.md` for
per-criterion semantics). Differences from legacy, all fail-fast:

- unknown criterion → `UnknownCriterionError` (legacy: silent `0.0`)
- `ruleset="fide-2026"` → the FIDE-2026 engine (`tiebreak_core.fide2026`):
  the fide-2024 Swiss core plus §16.4 dummy caps, an explicit
  `mode="swiss"|"round_robin"` regime flag (§15.2 carve-out),
  `draw_points=0.5` (§16.4.2 draw value), `forfeits_as_played=False`
  (MTB26 `/P` opt-in for BH/SB/FB/Koya/DE), terminal ranking stages
  `tpn` (needs `pairing_numbers={pid: n}`) and `rtng`, all as additive
  strict keyword arguments. Unknown rulesets → `UnsupportedRulesetError`.
- score not in {0, 0.5, 1}, color not in {"white", "black"},
  round_number < 0, rating < 0, points < 0/non-finite, mapping key !=
  `player_id` → `InvalidGameRecordError` / `InvalidPlayerDataError`
- unknown `kind`, or kind/opponent mismatch (explicit `played` with
  `-1`; bye-like kinds with a real opponent) → `InvalidGameRecordError`.
  Unspecified `kind` normalizes via `normalize_kind()` (`-1` →
  `unplayed`, else `played`). Legacy calculators ignore `kind`.
- `frozen_registry()` → immutable snapshot (`TypeError` on write)
- `register_criterion()` refuses built-in ids (`RegistryError`)

fide-2024 additionally requires: `total_rounds` = tournament rounds
(≥1); categorized unplayed rounds (legacy `-1` without kind is
rejected); supported criteria only (`arpo`, `buchholz_sum`,
`direct_encounter` → `UnsupportedCriterionError`).

## Adding a new tie-break

1. Add pure function `(player, all_players) -> float` in `calculators.py`.
2. Register id in `TIEBREAK_REGISTRY` + `registry.TIEBREAK_IDS`.
3. Add FIDE ref in `registry.TIEBREAK_FIDE_REF` (or mark non-FIDE).
4. Add optional Persian name ONLY in `display.py`.
5. Add unit + golden cases. If semantics differ from legacy, gate behind a
   NEW rules version — never change legacy outputs.
6. Verify: `pytest`, plus old-vs-new comparison if replacing a legacy id.
