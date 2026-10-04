# FIDE data semantics (missing / precision / Article 16 dependencies)

## 1. Value states (global model, ADR-004)

Every criterion output is one of: a valid number (including a valid
**zero**, e.g. Koya 0.0 with no qualifying opponents), or a typed
failure. `missing == 0` is forbidden unless the article says so:

| Situation | Representation | Example |
|---|---|---|
| Valid zero | `0.0` | Koya with no ≥50% opponents |
| No rated OTB opponents (TPR) | `0.0` (documented interpretation, not FIDE) | `tpr` |
| Empty ARO set | `0.0` (documented edge) | `aro` |
| Uncategorized `-1` round (fide-2024) | `InvalidGameRecordError` | strict gate |
| Unknown criterion (strict) | `UnknownCriterionError` | fail-fast |
| Unsupported criterion for ruleset | `UnsupportedCriterionError` | `arpo`/`buchholz_sum`/scalar-DE under fide-2024 |
| Unsupported ruleset | `UnsupportedRulesetError` | unknown ruleset id |

Ratings snapshot: the core receives ONE rating per player, defined as
the tournament-start (first) list — this satisfies the 2026
first-rating rule (D9) by construction. Consumers must not feed
mid-tournament re-ratings; the adapter contract states this.

## 2. Precision rules

- BH/SB/Koya/PS/WIN-family/REP: exact sums of halves — compute in
  exact arithmetic (halves are binary-exact; prefer `Fraction`/integer
  half-points where aggregation order could matter). Legacy rounding
  (BH 1dp, SB 2dp) is frozen calculation behavior, and ranking sorts
  the rounded values (KNOWN_LIMITATIONS 9) — never "fix" under legacy.
- ARO/APRO/APPO: round half-up to integer exactly once, after
  averaging. AOB: exact mean (no rounding — ranking sorts on it).
  (Legacy BH 1dp / SB 2dp rounding-before-ranking is frozen.)
- TPR: fractional score rounded half-up to hundredths → §8.1a lookup
  (documented interpretation); PTP: binary search on §8.1b bands, full
  scale, no ±400 cut.
- Float risk: §8.1a/8.1b table floats need tolerance-aware tests, not
  exact equality, at table boundaries.

## 3. Article 16 dependency matrix

| Criterion | §16.3 (opp scores) | §16.4 dummy | §16.5 cuts | 2026 caps |
|---|---|---|---|---|
| BH | yes | yes | C1/C2/M1/M2 | yes (16.4.1/16.4.2) |
| SB | yes (× score) | yes (× awarded) | SB-C1 higher-of | yes |
| FB | yes (on drawn final) | yes (FB points) | via cuts | yes |
| AOB | indirect (via opp BH) | — | — | indirect |
| Koya | qualification uses raw final points (face-value reading) | — | — | no |
| PS/WIN/WON/BPG/BWG/REP | — (own-record/OTB) | — | — | no (RR-mode §15.2 excepted) |
| ARO/TPR/PTP/APRO/APPO | OTB-only sets; 2026 RR: forfeits excluded (§15.2) | — | ARO-C1 | no |
| DE | forfeit exclusion §6.1.1 (Swiss) | — | — | no |
| STD (2026) | scheduled-opp scores (`opponent_score` or 1–½–0 complement) + draw value | unplayed-vs-draw comparison | — | IMPLEMENTED standard scope (exotic tables without explicit scores raise — U6) |

Game-kind → category mapping (implemented `classify()`): `played`→—;
`pairing_bye`→16.2.1; `forfeit_win`→16.2.2; `forfeit_loss`→16.2.4;
`requested_bye`→16.2.3/16.2.5 positionally (later participated round
= early), except a requested FULL-point bye →16.2.1 (full-point bye,
non-VUR — §16.1.1 defines requested byes as half/zero-point only);
`unplayed` (legacy generic)→rejected under fide-2024;
`absent`→no round (gap-filled by PS only). VUR = half/zero-point
requested/forfeit-loss kinds (§16.1.2).

## 4. Missing inputs per SPECIFIED criterion (model gaps)

All historical gaps below are closed; the section is kept as the
input-contract record:

- `std`: resolved in 0.8.0 — optional `GameRecord.opponent_score` +
  event draw value (`draw_points`); exotic tables without explicit
  scores raise (U6).
- `tpn` / `rtng`: resolved in 0.7.0 — `pairing_numbers` strict
  parameter for TPN; RTNG reads the rating snapshot; `/R` reversal
  in 1.1.0.
- 2026 `16.4.1` cap: resolved in 0.7.0 — scheduled opponent's
  Art-16.3-adjusted score from the players map (incl. trailing
  rounds); no model change was needed.
- Team criteria: resolved in 1.1.0 — full `TeamMatch` domain (see
  catalog) in `tiebreak_core.team`.
  scope, not a field addition.
