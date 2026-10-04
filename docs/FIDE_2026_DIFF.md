# FIDE 2024 → 2026 diff (verified)

Method: full-text word-level diff of two PRIMARY extractions:

- `A` — FIDE Council 2024_FC2_18 (approved 29/07/2024, applied 1 Aug 2024;
  local extraction `/tmp/fide2024.txt`, 652 lines).
- `B` — Play-Off and Tie-Break Regulations effective 1 Mar 2026
  (approved 02/02/2026; extracted pp.248–261 of the official
  FIDE Arbiters' Manual 2026, `arbiters.fide.com`).

Every other word-level difference is layout/typography noise
(`participant`→`player` in §§10.2–10.3, `topmost`→`top-most`,
`per this rule`→`in accordance with this rule`, list punctuation).
Only semantic deltas are listed below. Nothing else in C.07 changed:
§§6.2/6.3, 7.1–7.6, 9.x, 11, 12.1–12.3, 13.1/13.2/13.4, 14.x,
16.1–16.3, 16.5, 16.6 are word-identical.

## D1. Article 4.2 — subgroup sequencing (clarification)

- 2024: *"moving to the next in the list whenever a persisting tie
  cannot be broken."*
- 2026: *"moving to the next in the list for each subgroup of
  participants still tied."*
- Effect: the ordered list re-applies per remaining tied subgroup.
  No behavior change for the current engine (ranking already proceeds
  per subgroup via successive criteria), but it normatively settles
  that subgroups never inherit a resolved rank from a sibling subgroup.

## D2. Article 4.3 Type B — "results or data" (wording)

- 2024: *"participants' own results"* → 2026: *"participants' own
  results or data"*. Accommodates the new data-based criteria
  (TPN §7.8, RTNG §10.6). No calculation impact.

## D3. New criteria in the Article 5 table (additive)

| Name | Type | § | Acronym | Cut-1 |
|---|---|---|---|---|
| Standard Points | B | 7.7 | STD | — |
| Tournament Pairing Number | B | 7.8 | TPN | — |
| Rating | B | 10.6 | RTNG | — |

All other rows (types, sections, acronyms, Cut-1 flags) are unchanged.

## D4. §6.1 pointer "(for use in 6.2 and 6.3)" (clarification)

Mini-standings sentence gains an explicit pointer to the two use
sites. No semantic change; confirms the implemented reading
(ADR-008: mini-table feeds §6.2 reapplication and §6.3 certainty).

## D5. §7.7 Standard Points — NEW (individual/team bridge)

> *"The number of rounds in which a participant scores more points
> than their scheduled opponent, or obtains, without playing, more
> points than those awarded for a draw, plus half the number of rounds
> in which the participant scores the same number of points as their
> scheduled opponent, or obtains, without playing, the same number of
> points as awarded for a draw."*

Purpose (FIDE announcement 25 Mar 2026): restore the 1–½–0 framework
inside events with alternative scoring (e.g. 3–1–0). Required new
input: the **scheduled opponent's round score** (or the event's
draw-value table for unplayed rounds) — not derivable from
`GameRecord.score` alone. Implemented in 0.8.0 (`std` criterion +
optional `GameRecord.opponent_score`; standard 1–½–0 complement when
`draw_points == 0.5`, typed error for exotic tables without explicit
scores). Diff text kept as the original 2026-gap analysis.

## D6. §7.8 Tournament Pairing Number — NEW (terminal)

> *"Players are sorted according to their (final) tournament pairing
> number in ascending order. Alternatively, they can be sorted in
> reverse order (i.e. in descending order)."*

Deterministic lots-replacement at the end of a sequence. Required new
input: final pairing numbers (not in the current model).
Ownership: consumer-side sort key; implemented in 0.7.0 as a
terminal criterion once pairing numbers cross the boundary
(`pairing_numbers` strict parameter; `/R` reversal in 1.1.0).
Diff text kept as the original 2026-gap analysis.

## D7. Article 8 note — Buchholz banned from round-robins (NEW)

> *"Note: These tie-breaks must not be used in round-robins."*

Absent from the 2024 text (verified by search). Declarative scope
restriction covering BH and derivatives (§§8.1–8.3). Engine impact:
none under `fide-2024`; documented-not-enforced under `fide-2026`
by design — list selection is organizer-owned (C.07 §4.1/Art.8
note), partial round-robins exist (where a ban would over-reject),
and detection needs full pairing coverage. The `mode` flag keeps
regime selection explicit consumer-side.

## D8. §8.2 AOB — "(or Fore Buchholz)" (clarification)

- 2024: *"average of the Buchholz score of the opponents played over
  the board"* → 2026 adds *"(or Fore Buchholz)"*.
- Settles that AOB may average Fore-Buchholz values (e.g. computed
  live before the final round). The implemented `aob` (BH-based,
  final) is the default reading; an FB-based variant would be a new
  criterion id, not a silent change.

## D9. §10 preamble — multiple-rating rule (NEW)

> *"Note: These tie-breaks are not recommended when a player can get
> more than one rating during the tournament (e.g. due to multiple
> rating reports). If they are nevertheless chosen, the rating used to
> calculate them is the first one, unless the specific regulations of
> the tournament state otherwise."*

New normative input-selection rule for all of §§10.1–10.6.
Implementation consequence: rating inputs must be pinned to the
tournament-start (first) list; mid-tournament re-ratings must not
leak into ARO/TPR/PTP/APRO/APPO/RTNG. Currently the core receives a
single snapshot — compliant by construction; the contract must say so
(see `FIDE_DATA_SEMANTICS.md`).

## D10. §10.6 Rating (RTNG) — NEW (terminal)

> *"Players are sorted according to their rating, from highest to
> lowest. Alternatively, they can be sorted in reverse order (i.e. from
> lowest to highest)."*

Same ownership as TPN (§D6). Implemented in 0.7.0 as a terminal
ranking stage (`rtng`; `/R` reversal in 1.1.0). Diff text kept as
the original 2026-gap analysis.

## D11. §13.3.2 — four named EDE+knockout chains (NEW)

2024 ended at: *"…which ones and in what order."* 2026 appends:

- a. `EDEBT` → EDE + BC + TBR
- b. `EDEBB` → EDE + BC + BBE
- c. `EDET` → EDE + TBR
- d. `EDEB` → EDE + BBE

Team scope only; no individual-engine impact. Relevant if a team
module is ever built (names are then normative ids).

## D12. §15.2 — forfeit carve-out for pre-determined pairings (SEMANTIC)

- 2024: *"forfeit wins or losses (the only possible unplayed rounds)
  are treated as regular games."*
- 2026: *"treated as regular games **or matches, except that all
  forfeits in ratings-based tie-breaks (see Article 10) and forfeit
  losses in Type B tie-breaks (see Article 7) remain unplayed
  rounds**."*
- Effect (round-robins): forfeits are excluded from ARO/TPR/PTP/
  APRO/APPO opponent sets and denominators, and forfeit losses do not
  count in Type-B counts (notably BPG: a forfeit loss with Black is no
  longer a "game played with Black"). The `fide-2024` engine targets
  Swiss play and implements Article 16, not Article 15 — no change to
  existing behavior; a future round-robin mode must implement D12.

## D13. §16.4 — dummy caps (SEMANTIC, the main 2026 change)

- 2024: unplayed round = game vs a dummy *"that concluded the
  tournament with the same number of points as the participant
  themself"* (uncapped).
- 2026: *"The dummy's score … is the participant's own score.
  However, it shall not exceed:*
  - *16.4.1 the scheduled opponent's adjusted score (see Article
    16.3), for unplayed rounds of categories 16.2.2 and 16.2.4
    (forfeits);*
  - *16.4.2 the points awarded for a draw multiplied by the number of
    rounds in the tournament, for all other unplayed rounds
    (categories 16.2.1, 16.2.3 and 16.2.5)."*
- Verified against the five encoded official worked examples (BH OLD→NEW:
  57→55, 51→49.5, 64.5→63, 74→69; see corpus
  `tests/corpus/fide2026_unplayed.json`).
- Engine impact: `fide-2024` (uncapped) is correct and frozen; the caps
  are the core of the `fide-2026` ruleset (IMPLEMENTED in 0.7.0,
  Phase F26-1). Implementing them needs the **scheduled opponent's
  adjusted score** per forfeit round — for `forfeit_win/loss` games
  the model carries the scheduled opponent id, and the engine
  evaluates that opponent's Article 16.3 adjustment including rounds
  after the encounter. All five encoded NEW-regime expectations
  reproduce the Manual's printed numbers (BH 57→55, 51→49.5,
  64.5→63, 74→69, BH-C1 11.5; SB 37.25 unchanged).

## D14. §16 header "(Until 28th February 2026)" (EDITORIAL ANOMALY)

The 2026 Manual prints: *"16. Unplayed Rounds Management in Swiss
Tournaments (Until 28th February 2026)"*. In a document applied from
1 Mar 2026 this qualifier is contradictory (the live Handbook chapter
shows the title without it). The article body contains the new caps
(D13) and the annexed examples teach the new regime, so the body is
treated as the March-2026 rule and the parenthetical as a stale
editorial leftover. Recorded in the uncertainty register; re-verify
against the live Handbook when reachable.

## D15. Worked-examples annex (NEW, PRIMARY)

Six official unplayed-game examples (Manual pp.258–261): Laxman
(BH/SB/BH-C1 with OLD+NEW columns), Examples 01/03/04 (OLD/NEW BH
columns), Example 06 (= TEC exercise, BH-C1 11.5). (Examples 02/05
are docs-only: Ex02's wording is recorded in U3, Ex05 is genuinely
ambiguous per U4.) Encoded as corpus
`tests/corpus/fide2026_unplayed.json` (5 VERIFIED `fide-2024`
expectations + 5 VERIFIED `fide-2026` expectations since 0.7.0). Known example-text
slips recorded there (Ex02 "maximum" vs cap; Ex05 acknowledged
under-specification; Ex06 "2.5" vestige; EX04 Amit R2–R10
representation, see roadmap U11).
