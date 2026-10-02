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

## Complexity

- Per-player criterion: O(games). `buchholz_sum`: O(games²).
- `rank_standings`: O(n log n) sort + O(n · criteria · games) values.
- Fixed in 0.1.x: per-player `dict(players)` copy (O(n²) churn).

## Guidance

- Reuse one `rank_standings` call per standings publication; use
  `order_ids` when values are already computed.
- Future `fide-2026` work should precompute the opponent-score context
  once per standings (same pattern as the lookup fix) rather than
  recomputing per player.
- No external caching/infrastructure: the library stays dependency-free;
  memoization, if ever needed, belongs to callers with explicit keys
  (inputs + ruleset).
