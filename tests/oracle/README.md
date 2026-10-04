# Independent differential oracle (echecs)

Third-party oracle data for `tests/test_differential.py`. The suite
never runs node and never touches the network: it compares
tiebreak-core against the COMMITTED values in `echecs_4.1.json`.

## Oracle

[`echecsjs`](https://github.com/echecsjs) MIT-licensed tie-break
packages (zero runtime dependencies), дробно implementing FIDE C.07
(March-2026 text):

| Package | Version | Covers here |
|---|---|---|
| `@echecs/buchholz` | 4.1.0 | BH/C1/C2/M1/M2, Fore BH + C1/C2, AOB, AOB/FB |
| `@echecs/sonneborn-berger` | 4.1.0 | SB/C1/C2 |
| `@echecs/koya` | 4.1.1 | KS (base; limit variants exist but core has no limit API yet) |
| `@echecs/average-rating` | 4.1.0 | ARO/C1/C2 |
| `@echecs/progressive` | 4.1.0 | PS (PS-C1 EXCLUDED — see below) |
| `@echecs/direct-encounter` | 4.1.0 | mini-table scores on all-met groups |
| `@echecs/tournament` | 3.3.0 | shared types only |

## Known oracle divergences (do NOT "fix" tiebreak-core to match)

- **PS-C1**: echecs restarts accumulation without round 1; FIDE
  §14.1.1.c excludes the post-round-1 cumulative total. The official
  TEC PS/PS-C1 table (16/16 rows) matches tiebreak-core, refuting the
  oracle here. Excluded from comparison.
- **AOB/AOB-FB**: echecs rounds to integer (`Math.round`); core keeps
  exact means (§8.2 states no rounding). Compared with ±0.51 tolerance.
- **Degenerate sizes**: echecs cuts/empties small element sets (no
  keep-last guard; trims below spec minimums). All fixtures give every
  player ≥5 recorded rounds, keeping both engines in defined behavior.
- **Koya threshold basis**: compared on fully-played fixtures only.
  tiebreak-core qualifies on published final scores (§9.2 letter);
  echecs recomputes excluding byes. Documented; fully-played events
  cannot diverge.
- **Empty records**: fixtures are mutually coherent (every game on
  both sides, points == sums); the engines' missing-data policies are
  unit-tested separately, not differentially.
- **FB-M1/M2, ARO-M1/M2**: oracle computes them; core has no such ids
  (generic machine deferred) — harness asserts explicit
  `UnknownCriterionError`.

## Regenerating

```bash
cd tests/oracle
npm install @echecs/buchholz@4.1.0 @echecs/sonneborn-berger@4.1.0 \
  @echecs/koya@4.1.1 @echecs/average-rating@4.1.0 \
  @echecs/progressive@4.1.0 @echecs/direct-encounter@4.1.0 \
  @echecs/tournament@3.3.0
node driver_echecs.mjs fixtures/ > echecs_NEW.json
# review the diff criterion by criterion (see mismatch protocol in
# test_differential.py), then replace echecs_4.1.json
```

Never vendor `node_modules` into the repository. A regenerated bundle
must record its package versions in `meta.packages`.
