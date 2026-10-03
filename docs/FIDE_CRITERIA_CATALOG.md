# FIDE criteria catalog

One record per criterion/modifier. `Ruleset` = first C.07 edition
defining the current semantics; `Implemented` = tiebreak-core status
(see `docs/IMPLEMENTATION_ROADMAP.md` for the matrix).
Precision: sums are exact (halves are binary-exact; use exact
arithmetic, never float accumulation for ranking); only the noted
averages round, half-up, once, at the end.

## Opposition / score based (Article 8 + modifiers Article 14)

### BH — Buchholz §8.1 (Type C). Ruleset: Sep-2023; 2026 scope note.
Formula: Σ final adjusted scores (§16.3) of all opponents; own
unplayed rounds contribute the §16.4 dummy (2024: uncapped own score;
2026: caps 16.4.1/16.4.2). Inputs: opponent final scores, own rounds
with kinds. 2026: *"must not be used in round-robins."*
Implemented: `buchholz` (legacy + fide-2024).

### BH-C1 / BH-C2 — Cut-1 §14.1.1.a / Cut-2 §14.2 (Type C).
Drop the 1 (resp. 2) least-significant opponent-score values, with the
§16.5 VUR exception (cut lowest VUR contribution first, reapplied per
cut §16.5.2). Edge: never cut the last remaining element (documented).
Implemented: `buchholz_cut1`, `buchholz_cut2` (both rulesets paths).

### BH-M1 / BH-M2 — Median §§14.3/14.4 (Type C).
Drop least then most (M1); two least then two most (M2), each subject
to §16.5. Fallbacks: <3 (M1) / <5 (M2) scores → full BH (documented
edge, not a FIDE rule — FIDE assumes full Swiss coverage).
Implemented: `median_buchholz`, `median_buchholz_2`.

### AOB — Average of Opponents' Buchholz §8.2 (Type CC).
Mean of the (Fore-)Buchholz values of opponents played over the
board (2026 "(or Fore Buchholz)" = live-FB variant allowed).
Implemented: `aob` (exact mean, no rounding — FIDE states none and
ranking sorts on the exact value).

### FB — Fore Buchholz §8.3 (Type D).
BH computed as if all paired final-round games were draws, then
Article 16 on top; own dummy uses FB-adjusted own points.
Implemented: `fore_buchholz` (fide-2024).

### SB — Sonneborn-Berger §9.1 (Type BC).
Σ over rounds: opponent final adjusted score × points scored against
them; own unplayed rounds = dummy × awarded points (§16.4, 2026 caps
apply). Implemented: `sonneborn_berger` (legacy 2dp / fide-2024
exact), `sonneborn_berger_cut1` (§14.1.1.d opponent-score
identification + §16.5.1 higher-of rule, fide-2024; SB-C2 reapplies
per §16.5.2 under fide-2026).

### KS — Koya System §9.2 (Type BC, round-robin scope).
Points scored against opponents finishing on ≥50% of the maximum
possible tournament score (raw final points qualify). Limit
modifiable by half-points (§14.5; e.g. echecsjs `koya±½/±1`).
FIDE scopes Koya to round-robins; the core applies the arithmetic
wherever requested and leaves scope gating to the caller (documented).
Implemented: `koya` (threshold on maximum-possible = total rounds).

### PS / PS-C1 — (Sum of) Progressive Scores §7.5 (Type B).
Σ of the participant's cumulative score after each round (gap-filled:
absent rounds carry the last score). PS-C1 (§14.1.1.c) excludes the
score after round 1. (Generic Cut-2/median readings exist in software,
e.g. echecsjs `progressiveCut2`, but FIDE names only PS-C1.)
Implemented: `progressive`, `progressive_cut1` (fide-2024).

## Own-record (Type B, Article 7)

### WIN §7.1 — rounds with win-points, with or without playing.
Implemented: `wins` (legacy + fide-2024; same numbers here).
2026 interaction: §15.2 keeps forfeit losses as unplayed in Type B —
no WIN change (losses never counted), but BPG-class counts change in
round-robins (see WON/BPG below).

### WON §7.2 — games won over the board. Implemented: `won`
(fide-2024; legacy `wins` over-counts byes/forfeits).

### BPG §7.3 / BWG §7.4 — OTB games (wins) with Black.
Implemented: `games_black`, `wins_black` (fide-2024 OTB-only).
2026 D12: in pre-determined-pairing events forfeit losses stay
unplayed → excluded from BPG (a fide-2026 RR-mode rule).

### REP §7.6 — rounds minus half/zero-byes and forfeit losses.
Implemented: `rounds_elected` (fide-2024).

### STD §7.7 — Standard Points (NEW 2026, Type B). SPECIFIED.
Rounds outscoring the scheduled opponent (+½ for equal), unplayed
rounds compared against the event's draw value. Needs scheduled
opponent round scores — missing input (see `FIDE_DATA_SEMANTICS.md`).

### TPN §7.8 — Tournament Pairing Number (NEW 2026, Type B). SPECIFIED.
Ascending (or, if regulated, descending) final pairing number.
Terminal lots-replacement. Needs pairing numbers — consumer input.

## Direct Encounter (Article 6, Type A, multi-listable)

Group-level ranking stage, not a scalar. Algorithm (implemented under
fide-2024, ADR-008): (1) form the tied group; (2) mini-standings from
played mutual encounters only (Swiss forfeit exclusion §6.1.1 unless
regulations opt in; repeated-meeting averages §6.1.2, exact
arithmetic; Art 4.4 multi-count otherwise); (3) complete meeting →
standings decide, subsets reapply §6.2 until stable; (4) incomplete
meeting (Swiss) → certainty ranking §6.3 (alone-at-top whatever the
missing results, iteratively), then reapply to the remainder.
Termination: guaranteed (each reapplication strictly shrinks the
unresolved set or exhausts §6.2/§6.3; leftover ties fall through to
the next criterion / lots per Art 4.2). Scalar `direct_encounter`
raises `UnsupportedCriterionError` under fide-2024 (no per-player
value exists). Team EDE (§13.3 + 2026 chain names EDEBT/EDEBB/EDET/
EDEB) is team-module scope, not core scope.

## Rating / performance (Article 10)

Common rules: dropped when unrateds are present unless the tournament
pre-publishes unrated handling (§10 preamble); multi-rating events
use the FIRST rating (2026, D9 — core-compliant by single-snapshot
construction); PTP uses the FULL scale, no ±400 cut (§10.3 — immune
to the Oct-2025 400/2650 rating-calc amendment, which never touched
the tables anyway); B.01 norm-TPR (floors, imputed 1400, 35% minimum)
is a different object and must never share code.

### ARO §10.1 (Type D). Mean OTB opponent rating, half-up integer.
2026 D12 excludes forfeits (RR mode). Implemented: `aro`,
`aro_cut1` (§14.1.1.b, <2 rated OTB opponents → uncut).

### TPR §10.2 (Type DB). Rounded ARO + table RD for the OTB
fractional score (Rating Regulations §8.1a, 101 entries, verified
stable 2022→2024→now). Fraction rounded half-up to hundredths
(documented interpretation); no rated OTB games → 0.0 (documented,
not FIDE). Implemented: `tpr`.

### PTP §10.3 (Type DB). Lowest rating with Σ §8.1b probabilities ≥
tournament (OTB) score; zero score → 800 below lowest rated
opponent; binary search over the full scale. Implemented: `ptp`
(documented OTB-points target reading).

### APRO §10.4 / APPO §10.5 (Type DC). Mean of opponents' TPR/PTP,
half-up integer. Implemented: `apro`, `appo`.

### RTNG §10.6 (NEW 2026, Type B). SPECIFIED. Rating order,
descending (or ascending if regulated). Terminal; same ownership as
TPN.

## Team systems (Articles 11–13) — OUT_OF_SCOPE for the core

Primitives: MP + GP per team match (§11). Knockout: BC (board-number
× board GP, lower wins, GP-tied only), TBR (top-board GP, reapplied
downward), BBE (all-but-bottom GP, reapplied upward) — all need a
per-board GP matrix. Competition: MPvGP (§13.1), ESB four combos
EMMSB/EMGSB/EGMSB/EGGSB (§13.2 + Cut-1 variant §14.1.2), EDE
(§13.3.1 primary→secondary, §13.3.2 2026 chains, §13.3.3 subset
restart), SSSC (secondary + BH-derived Schedule Strength ÷
truncated normaliser, §13.4). §13 blanket rule re-applies Arts.6–10
to teams on MP/GP reference scores. All need `TeamMatch`
(round/opponent-team/MP/GP/board vector/unplayed flags) — a different
record type; `GameRecord` must not be stretched (see gap analysis).

## Modifiers (Article 14) — summary

Cut-1 §14.1 (BH-C1/ARO-C1/PS-C1/SB-C1 + team-ESB variant §14.1.2),
Cut-2 §14.2 (BH-C2), Median-1 §14.3, Median-2 §14.4, Limit §14.5
(Koya threshold ±½ steps), all subject to Article 16. Generic
modifier machinery beyond the named FIDE combinations is
software convention (e.g. PS-C2, ARO-M1/M2 in echecsjs) —
SPECIFIED at most, never presented as FIDE-defined.

## Non-FIDE / legacy ids (frozen, never extended)

`buchholz_sum` (non-FIDE extension), `arpo` (legacy simplified dp,
superseded by `apro`), legacy `direct_encounter` scalar stub (0.0).
Frozen under `legacy-0.1.0` forever.
