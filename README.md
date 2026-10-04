# tiebreak-core

[![CI](https://github.com/20kevit/tiebreak-core/actions/workflows/ci.yml/badge.svg)](https://github.com/20kevit/tiebreak-core/actions/workflows/ci.yml)

Standalone Python library for chess tie-break calculation, implementing the applicable FIDE C.07 semantics for individual and team tournaments.

Pure Python. Zero runtime dependencies. Deterministic. MIT licensed.

## What it is

`tiebreak-core` computes chess tie-break values and orderings from normalized tournament data you supply: per-player game records (individual) or per-team match records (team). It implements the FIDE C.07 calculation semantics — Buchholz families, Sonneborn-Berger, progressive scores, Koya, rating-based criteria, Direct Encounter, team systems (MP/GP, Board Count, Extended Sonneborn-Berger, Extended Direct Encounter, SSSC), and the generic MTB26 modifier machine (`/Cn`, `/Mn`, `/L±n`, `/P`, `/F`, `/R`, `:MP/:GP`) — under explicit, versioned rulesets.

## What it is NOT

Not a tournament manager, not a pairing engine, not a rating calculator, not a TRF file parser, not a web service, not a database layer. It owns calculation and ordering only; seeding, pairing, persistence, and file I/O belong to consumers. It is **not FIDE-approved software** — no such claim is made (see [FIDE conformity](#fide-conformity) below).

## Why it exists

Tournament applications (`chess-manager`, `pairing-core` integrations, future tools) all need the same FIDE tie-break arithmetic. `tiebreak-core` is the shared, independently testable home for it, with frozen ruleset semantics so historical results never shift under callers.

## Features

- **Individual Swiss / Round Robin / pre-determined pairings** — Article 16 unplayed-round management (categories, adjusted scores, capped/uncapped dummies, VUR-aware cuts), Swiss vs RR forfeit scope flag.
- **Team tournaments** — full C.07 Articles 11–13 on a dedicated `TeamMatch`/`TeamRecord` model.
- **Generic modifiers** — any valid MTB26 descriptor (`BH/C3`, `ARO/M2`, `KS/L+1`, `SB/C2/P`, `TPN/R`), with typed rejection of FIDE-undefined combinations.
- **Explicit rulesets** — `legacy-0.1.0` (frozen), `fide-2024` (frozen), `fide-2026` (current). Same input + same ruleset → same output, forever.
- **Typed failures** — `UnknownCriterionError`, `UnsupportedCriterionError`, `InvalidDescriptorError`, `InvalidGameRecordError`, `InvalidPlayerDataError`, and more. No silent fallback on the strict path.
- **Deterministic ranking** — staged ordering (points → criteria → group stages → explicit keys), no mutation of caller data.

## FIDE scope

| Area | Status |
|---|---|
| Individual criteria, C.07 Arts. 6–10 + modifiers Art. 14 | Implemented (`fide-2024`, `fide-2026`) |
| Unplayed rounds, Art. 16 (both editions) + RR §15.2 carve-out | Implemented |
| Team criteria, Arts. 11–13 (MP/GP, BC/TBR/BBE, MPvGP, ESB×4, EDE+chains, SSSC) | Implemented |
| Rating tables (§§8.1a/8.1b), ARO/TPR/PTP/APRO/APPO/RTNG | Implemented |
| Direct Encounter (§6) / Extended DE (§13.3) as group stages | Implemented |
| Play-off formats (Art. 3), pairing-time evaluation (C.04), norm calculations (B.01) | Consumer-owned / out of scope |
| Exotic scoring tables without explicit per-round scores | Rejected with a typed error |

Details: `docs/FIDE_COMPLETE_REQUIREMENTS_MATRIX.md`. Limitations: `docs/KNOWN_LIMITATIONS.md`.

## Rulesets

```python
from tiebreak_core import available_rulesets
for rs in available_rulesets():
    print(rs.id, "-", rs.status)
# legacy-0.1.0 - implemented (frozen behavior-preserving extraction)
# fide-2026 - implemented     (current C.07: §16.4 caps, RR mode, TPN/RTNG, /P)
# fide-2024 - implemented     (frozen era semantics)
```

See `docs/VERSIONING.md` for the frozen-ruleset policy.

## Installation

Requires Python ≥ 3.10. No dependencies.

```bash
pip install tiebreak-core
```

From source:

```bash
pip install -e .
```

## Quick start — individual Swiss

```python
from tiebreak_core import (
    GameRecord, PlayerTiebreakData,
    calculate_all_strict, rank_standings_strict,
)

players = {
    1: PlayerTiebreakData(1, 2000, 2.5, [
        GameRecord(2, 1900, 1.0, "white", 1, kind="played"),
        GameRecord(3, 1950, 0.5, "black", 2, kind="played"),
        GameRecord(4, 1800, 1.0, "white", 3, kind="played"),
    ]),
    2: PlayerTiebreakData(2, 1900, 1.0, [
        GameRecord(1, 2000, 0.0, "black", 1, kind="played"),
        GameRecord(4, 1800, 1.0, "white", 2, kind="played"),
        GameRecord(3, 1950, 0.0, "black", 3, kind="played"),
    ]),
    3: PlayerTiebreakData(3, 1950, 2.0, [
        GameRecord(4, 1800, 1.0, "white", 1, kind="played"),
        GameRecord(1, 2000, 0.5, "white", 2, kind="played"),
        GameRecord(2, 1900, 0.5, "white", 3, kind="played"),
    ]),
    4: PlayerTiebreakData(4, 1800, 0.0, [
        GameRecord(3, 1950, 0.0, "black", 1, kind="played"),
        GameRecord(2, 1900, 0.0, "black", 2, kind="played"),
        GameRecord(1, 2000, 0.0, "black", 3, kind="played"),
    ]),
}
criteria = ["buchholz_cut1", "sonneborn_berger"]

values = calculate_all_strict(players[1], players, criteria,
                              total_rounds=3, ruleset="fide-2026")
# {'buchholz_cut1': 3.0, 'sonneborn_berger': 2.0}

standings = rank_standings_strict(players, criteria, total_rounds=3,
                                  ruleset="fide-2026")
print([p.player_id for p in standings.players])  # [1, 3, 2, 4]
```

Game kinds (`played`, `pairing_bye`, `forfeit_win`, `forfeit_loss`, `requested_bye`, …) drive Article 16 handling — see `docs/FIDE_DATA_SEMANTICS.md`. More: `examples/a_individual_swiss.py`, `examples/b_individual_round_robin.py`.

## Team tournaments

```python
from tiebreak_core import (
    TeamFormat, TeamMatch, TeamRecord,
    calculate_team_strict, rank_teams_strict,
)

fmt = TeamFormat(mp_win=2.0, mp_draw=1.0)
teams = {
    1: TeamRecord(1, 3.0, 5.0, [
        TeamMatch(2, 1, 2, 3.0),
        TeamMatch(2, 2, 1, 2.0)], (2.5, 1.5, 0.5, 0.5)),
    2: TeamRecord(2, 1.0, 3.0, [
        TeamMatch(1, 1, 0, 1.0),
        TeamMatch(1, 2, 1, 2.0)], (1.5, 0.5, 0.5, 0.5)),
}

emmsb = calculate_team_strict(teams[1], teams, "EMMSB",
                              total_rounds=2, fmt=fmt)  # 3.0
standings = rank_teams_strict(teams, ["EMMSB", "EDE", "BC"],
                              total_rounds=2, fmt=fmt)
```

Board totals (`board_points`) back the §12 codes; forfeit/PAB legs are recorded at standard-win values per the §12 intro. More: `examples/c_team_tournament.py`.

## Generic modifiers

```python
from tiebreak_core import (
    calculate_descriptor_strict, rank_descriptors_strict, parse_descriptor,
)

parse_descriptor("SB/C2/P")   # base SB + Cut-2 + forfeit inclusion
calculate_descriptor_strict(player, players, "BH/C3", total_rounds=9,
                            ruleset="fide-2026")
rank_descriptors_strict(players, ["BH/C1", "SB/C1", "DE", "TPN/R"],
                        total_rounds=9, ruleset="fide-2026",
                        pairing_numbers={...})
```

`n=1/2` resolve to the named implementations (equivalence-tested); arbitrary valid `n`, `/L±n` Koya limits, and `/R` terminal reversal work uniformly. Invalid combinations raise `InvalidDescriptorError`. More: `examples/d_generic_modifier.py`, `examples/e_invalid_modifier.py`.

## Ruleset selection and Article 16 policy

Pass `ruleset=` explicitly on the strict path (`legacy-0.1.0`, `fide-2024`, `fide-2026`); `mode="round_robin"` selects the §15.2 regime under `fide-2026`. Unplayed-round policy is inspectable as data:

```python
from tiebreak_core import resolve_policy
resolve_policy("fide-2026")                        # capped 2026 dummies
resolve_policy("fide-2026", mode="round_robin")    # §15.2 forfeit scope
resolve_policy("fide-2026", late_bye_value=0.0)    # explicit §16.6 override
```

More: `examples/f_article16_policy.py`, `examples/g_deterministic_ranking.py`.

## Error handling

Every failure is typed and actionable: unknown criteria (`UnknownCriterionError`), unimplemented combinations (`UnsupportedCriterionError`), malformed descriptors (`InvalidDescriptorError`), bad records (`InvalidGameRecordError` / `InvalidPlayerDataError`), bad rulesets (`UnsupportedRulesetError`), registry misuse (`RegistryError`). The legacy path preserves its frozen lenient behavior; new code should use the strict path.

## Determinism and correctness

Same input + same ruleset → same output. Calculations never mutate caller data. Ranking sorts exact internal values (presentation rounding never decides order). The suite covers official FIDE worked values, definition-derived hand calculations, differential comparison against an independent engine, property/metamorphic invariants, invalid-input matrices, and benchmarks.

## Validation and evidence

- `tests/corpus/` — official FIDE worked examples (each case names its source).
- `tests/test_differential.py` — independent-oracle comparison harness.
- `tests/test_examples.py` — every `examples/*.py` script executes in CI.
- Evidence classes (`PRIMARY_NORMATIVE`, `OFFICIAL_VALUE`, `INDEPENDENT_ORACLE`, `PROJECT_DERIVED`) are defined in `docs/FIDE_SOURCE_REGISTRY.md` and never mixed.

## Architecture

```
consumer (chess-manager, pairing-core callers, your app)
   │  plain dataclasses in, immutable results out
   ▼
tiebreak_core
  modifiers  → MTB26 descriptor parsing + generic cut/median engine
  fide2026 / fide2024 → individual calculation engines (versioned)
  team       → team domain (§§11–13) on TeamMatch records
  ranking    → pure staged ordering (scalar / group / terminal stages)
  strict     → validated boundary with typed errors
  article16 / scoring → policy + point-table models
  registry / rules / errors / models / display
```

Details: `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/adr/`.

## Package / API overview

Top-level exports (~100 names): input models (`GameRecord`, `PlayerTiebreakData`, `TeamMatch`, `TeamRecord`, `TeamFormat`), calculators (`calculate*`, `calculate_descriptor*`, `calculate_team*`), ranking (`rank_standings*`, `rank_descriptors*`, `rank_team_standings*`, `order_ids*`), rulesets (`available_rulesets`, `describe_ruleset`), policy/scoring (`resolve_policy`, `ScoringScheme`), and all error types. Full surface: `docs/API.md`.

## Documentation map

| Document | Purpose |
|---|---|
| `docs/API.md` | Complete API reference with examples |
| `docs/ARCHITECTURE.md` | Boundaries, layers, dependency direction |
| `docs/FIDE_CRITERIA_CATALOG.md` | Per-criterion formulas and status |
| `docs/FIDE_TIEBREAK_MODIFIERS.md` | Modifier inventory (`/Cn /Mn /L /P /F /R /Kx / :MP/:GP`) |
| `docs/FIDE_MTB26_CATALOG.md` | MTB26 descriptor table + core-request boundary |
| `docs/FIDE_SOURCE_REGISTRY.md` | Auditable source index with evidence classes |
| `docs/FIDE_2026_DIFF.md` | 2024→2026 word-level diff (D1–D15) |
| `docs/KNOWN_LIMITATIONS.md` | Explicit scope boundaries |
| `docs/VERSIONING.md` | Ruleset vs package versioning policy |
| `docs/DEVELOPMENT.md` | Development and testing guide |
| `CHANGELOG.md` | Release notes |

## FIDE references

Normative basis: FIDE Handbook C.07 Play-Off and Tie-Break Regulations (editions effective 1 Aug 2024 and 1 Mar 2026), the MTB26 mandatory tie-break table, FIDE Rating Regulations §§8.1a/8.1b, and FIDE TEC worked examples. Full index: `docs/FIDE_SOURCE_REGISTRY.md`.

## FIDE conformity

This library **implements the applicable FIDE C.07 calculation semantics** within its documented scope and is **validated against authoritative FIDE material** (official worked values, definition-derived tests, independent differential checks). It is **not FIDE-approved, certified, or endorsed** — approval attaches to complete tournament-helper programs through FIDE's own process (see `docs/FIDE_APPROVAL_PATH.md`), never to a calculation library alone.

## Known limitations (summary)

Exotic scoring tables require explicit per-round opponent scores (typed error otherwise); the Buchholz round-robin restriction is documented, not enforced (organizer list duty); team edge readings without retrieved official examples are documented `PROJECT_DERIVED` interpretations; rating inputs must be the tournament-start snapshot (consumer contract). Full list: `docs/KNOWN_LIMITATIONS.md`.

## Development and testing

```bash
pip install -e .
python -m pytest tests -q        # full suite
python -m pytest tests/test_examples.py -q   # examples gate
```

See `docs/DEVELOPMENT.md`. CI runs Python 3.10–3.12 plus a packaging smoke test.

## Contributing

Issues and pull requests are welcome. Preserve frozen-ruleset outputs (see `docs/VERSIONING.md`), keep the dependency footprint at zero, add regression coverage for behavior changes, and never claim FIDE approval.

## License

MIT — see `LICENSE`.

## Status

Current release: **1.2.0** (`docs/VERSIONING.md`, `CHANGELOG.md`). Stable public API; additive extensions only — output-changing corrections to published rulesets require new ruleset ids (sole pre-publication exception: the F4 DE mini-table correction, documented in `CHANGELOG.md`).
