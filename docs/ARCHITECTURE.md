# Architecture

```
chess-manager ──adapter──▶ tiebreak-core ◀── (future) pairing-core / CLI / tests
pairing-core ──✕──▶ tiebreak-core   (no dependency, by design)
```

## Layers

- `models.py` — inputs (`GameRecord`, `PlayerTiebreakData`, plain `int` ids,
  mutable as in the original) + immutable outputs (`PlayerResult`,
  `StandingsResult`). No framework imports.
- `calculators.py` — pure functions `(player, all_players[, total_rounds])`.
  Bodies verbatim from chess-manager. `calculate` (one) and `calculate_all`
  (many) never rank.
- `ranking.py` — pure ordering over EXPLICIT policy:
  `sort_key(points, values, criteria, deterministic_key)`,
  `rank_standings(...)`, `order_ids(...)`. No `current_round`, no seeding,
  no `status` filtering.
- `strict.py` — OPTIONAL fail-fast surface (Phase 0, additive):
  `calculate_strict` / `calculate_all_strict` / `rank_standings_strict` /
  `order_ids_strict` validate inputs (criterion, ruleset, scores, colors,
  rounds, mapping integrity) and DELEGATE to the legacy functions, so
  values/order are identical. Unknown criteria raise
  `UnknownCriterionError` here (legacy yields 0.0, frozen). `ruleset=`
  accepts only supported versions; `"fide-2026"` is reserved and raises
  `UnsupportedRulesetError` until implemented.
- `errors.py` — typed error taxonomy (`TiebreakError` base). Raised only
  on the strict path and by `register_criterion`; legacy path never raises.
- `registry.py` — stable identifiers + FIDE cross-reference + default
  criteria. No display strings. Plus controlled extension:
  `frozen_registry()` (immutable snapshot view),
  `register_criterion()` (refuses built-in overwrite),
  `unregister_criterion()` (custom-only removal), `is_known()`.
  The legacy mutable `TIEBREAK_REGISTRY` in `calculators.py` is preserved
  for compatibility; new code should read via `frozen_registry()`.
- `display.py` — OPTIONAL Persian names. Never imported by calc/ranking.
- `rules.py` — `CALCULATION_RULES_VERSION = "legacy-0.1.0"`,
  `SUPPORTED_RULESETS`, `is_supported()`. Future rulesets (FIDE_2024/2026)
  must be new versions + new code paths, never edits to legacy behavior.

## Concept split (final decision)

```
tie-break calculation  (tiebreak-core: calculators)
ranking comparator     (tiebreak-core: ranking, explicit policy only)
tournament seeding     (chess-manager: current_round==0 rating/start_number branch)
```

Rationale: seeding depends on tournament lifecycle (`current_round`,
`rating_snapshot`, `start_number`, registration `status`). Keeping it in
chess-manager avoids over-coupling the core to one manager's lifecycle.
`rank_standings` takes an explicit `deterministic_keys` map instead.

## Dependency rules

- `src/tiebreak_core` imports stdlib only (`dataclasses`, `typing`).
- NEVER: flask, sqlalchemy, jinja, http, db sessions, chess-manager,
  pairing-core, network, disk.
- Tests may read the chess-manager repo for live old-vs-new comparison,
  but the package never does.

## Phase 0 notes

- `rank_standings` builds the shared player lookup ONCE (was: `dict()`
  copy per player). Measured 7-round synthetic: 2000 players 0.349s →
  0.075s; values/order unchanged (goldens pin them).
- `ruleset="fide-2026"` is a RESERVED name only. No FIDE-2026 code
  exists; requesting it raises `UnsupportedRulesetError`.
- `pairing-core` and `tiebreak-core` are independent: neither imports
  the other. chess-manager composes both (pairing for rounds, tie-break
  for standings) through thin adapters. No shared tournament-core.
