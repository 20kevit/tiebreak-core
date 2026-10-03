# Performance

Policy: correctness first, then performance. Numbers below are from
`tests/test_benchmarks.py` (7-round synthetic, 4-criterion chain) on the
mission machine — relative comparisons matter, absolute times do not.

## Measured (this mission)

| Players | Before shared lookup | After | Suite bound |
|---|---|---|---|
| 100 | 0.002s | 0.002s | — |
| 500 | 0.016s | 0.011s | — |
| 2000 | 0.349s | 0.075s | < 30s |

fide-2026 full ranking (0.7.0, 7-round kind-annotated synthetic,
6-criterion chain incl. `direct_encounter` + `rtng`, shared
classification/adjusted-score context built once per standings):

| Players | fide-2026 rank_standings | Suite bound |
|---|---|---|
| 100 | 0.02s | — |
| 500 | 0.05s | — |
| 2000 | 0.22s | < 60s |

## Complexity

- Per-player criterion: O(games). `buchholz_sum`: O(games²).
- `rank_standings` (legacy): O(n log n) sort + O(n · criteria · games).
- `fide2026.rank_standings`: one O(n · games) classification +
  adjusted-score precompute shared by all criteria, then the same
  linearithmic ranking. (Pre-fix prototype rebuilt the context per
  (player, criterion) — quadratic, ~1.6s at n=100; sharing gives ~80×.)
- `fide2024.rank_standings` still rebuilds its context per
  (player, criterion) — quadratic, acceptable at club sizes, known
  limitation for 2000-player opens under `fide-2024` (identical
  outputs; perf-only fix deferred, never a behavior change).
- Fixed in 0.1.x: per-player `dict(players)` copy (O(n²) churn).

## Guidance

- Reuse one `rank_standings` call per standings publication; use
  `order_ids` when values are already computed.
- No external caching/infrastructure: the library stays dependency-free;
  memoization, if ever needed, belongs to callers with explicit keys
  (inputs + ruleset).
