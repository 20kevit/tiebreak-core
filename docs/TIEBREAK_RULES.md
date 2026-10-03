# Tie-break rules reference

Two rulesets exist. Legacy (`legacy-0.1.0`) is a frozen extraction
(divergences below are preserved, NOT fixed). `fide-2024` implements
the cited FIDE articles for individual Swiss tournaments
(basis: FIDE Council 2024_FC2_18; see `docs/FIDE_SOURCES.md` item 0).

## fide-2024 semantics per criterion id

| id | FIDE | Semantics (deltas vs legacy) |
|---|---|---|
| buchholz | §8.1 + §§16.3–16.4 | Σ adj(opp) for played; own points (dummy) per unplayed round. Exact (no rounding). |
| buchholz_cut1/cut2 | §14.1.1.a/§14.2 + §16.5 | VUR-preferential cuts, reapplied (§16.5.2). Keeps ≥1 element (edge). |
| median_buchholz/_2 | §§14.3–14.4 + §16.5 | Least (VUR rule) then most. <3 / <5 elements → full BH (edge). |
| sonneborn_berger | §9.1 + §§16.3–16.4 | Σ adj(opp)×score; dummy own×awarded. Exact. |
| sonneborn_berger_cut1 | §14.1.1.d + §16.5.1 | Cut higher of (lowest VUR contribution, least significant). |
| progressive | §7.5 | Gap-filled over all tournament rounds (absent carries). |
| progressive_cut1 | §14.1.1.c | PS minus score after round 1. |
| wins | §7.1 WIN | Rounds with win-points incl. unplayed (same numbers as legacy here). |
| won | §7.2 WON | Over-the-board wins only (legacy `wins` counts byes/forfeits). |
| games_black | §7.3 BPG | OTB black games only (legacy counts unplayed sides). |
| wins_black | §7.4 BWG | OTB wins with black only. |
| rounds_elected | §7.6 REP | Recorded non-absent rounds minus half/zero-byes and forfeit losses. |
| aro | §10.1 ARO | OTB rated opponents; 0.5 rounded UP (legacy uses banker's). Unrated excluded; empty → 0.0. |
| aro_cut1 | §14.1.1.b ARO-C1 | Exclude lowest rating; <2 rated OTB opponents → uncut ARO (edge). |
| aob | §8.2 AOB | Mean of OTB opponents' fide-2024 BH, 1dp (presentation choice). |
| fore_buchholz | §8.3 FB | Final-round *paired* games as draws; Art.16 on top; dummy uses FB-adjusted own points. |
| koya | §9.2 KS | Opponents on ≥50% of maximum possible (total rounds); raw points qualify; all real-opponent games count. Applied wherever requested (FIDE scopes Koya to RR). |
| tpr | §10.2 TPR | Rounded ARO + §8.1a table difference for OTB fraction (fraction rounded half-up to hundredths — documented interpretation, not FIDE text). No rated OTB games → 0.0 (documented edge, not FIDE). |
| ptp | §10.3 PTP | Lowest rating with Σ §8.1b probabilities ≥ OTB points (documented target reading); zero target → 800 below lowest rated opponent; full scale, binary search. |
| apro/appo | §§10.4–10.5 APRO/APPO | Mean of OTB opponents' TPR/PTP, 0.5 rounded up. |
| direct_encounter | §6 DE (group-level) | Mini-standings over tied groups: played games only (Swiss forfeit exclusion §6.1.1), repeated-meeting averages §6.1.2, subset reapplication §6.2, Swiss certainty ranking §6.3. Ranking stage, not a scalar (no per-player value; see ADR-008). |
| arpo/buchholz_sum/direct_encounter | — | NOT in fide-2024 (`UnsupportedCriterionError`): rating tables unretrieved / non-FIDE / needs Phase-3 group architecture. |

Uncategorized unplayed rounds (legacy `-1` without kind) are rejected
under fide-2024 — categories must be explicit (see ADR-006). Art.16.6
local overrides are unsupported. Team systems are out of scope.

## legacy-0.1.0 (informational — v0.1.0 does NOT reimplement FIDE)

Authoritative source: FIDE Handbook C.07 Play-Off and Tie-Break
Regulations (effective 1 Aug 2024 → 28 Feb 2026; successor from 1 Mar 2026).

| Core id | FIDE | Notes |
|---|---|---|
| buchholz | §8.1 BH | verbatim legacy |
| buchholz_cut1 | §14.1a BH-C1 | verbatim legacy |
| buchholz_cut2 | §14.2 BH-C2 | verbatim legacy |
| median_buchholz | §14.3 BH-M1 | verbatim legacy |
| median_buchholz_2 | §14 BH-M2 | additive (0.2.x); <5 scores → full BH (documented edge) |
| sonneborn_berger | §9.1 SB | verbatim legacy (2dp) |
| progressive | §7.5 PS | verbatim legacy |
| wins / wins_black / games_black | §§7.1–7.4 | verbatim legacy |
| aro | §10.1 ARO | verbatim legacy |
| arpo | §10.4 APRO | legacy simplified dp — see KNOWN_LIMITATIONS |
| koya | §9.2 KS | FIDE specifies round-robin; legacy applies to Swiss |
| direct_encounter | §6 DE | legacy standings value is a 0.0 stub |
| buchholz_sum | — | non-FIDE extension, preserved |

Unplayed rounds (Art.16: categories, virtual-opponent draws-forth, Cut-1
exception) are NOT implemented in v0.1.0 — see KNOWN_LIMITATIONS.md.

March-2026 edition: implemented as `fide-2026` (0.7.0/0.8.0) — see
`docs/FIDE_2026_DIFF.md` (D1–D15: STD/TPN/RTNG, RR-ban note, AOB-FB
note, first-rating rule, EDE chain names, §15.2 carve-out, §16.4 dummy
caps, worked-examples annex). `fide-2024` behavior is unaffected and
frozen; the caps/examples are covered by corpus
`tests/corpus/fide2026_unplayed.json` (VERIFIED 2024 + VERIFIED 2026
values since 0.7.0).
Roadmap (new rules versions, never silent changes): all items shipped
(Art.16 both editions, SB-C1/PS-C1/ARO-C1 + C2 combos, Median-1/2,
AOB + AOB/FB, ForeBH + C1/C2, TPR/PTP/APRO/APPO/RTNG, full DE stage,
STD, TPN) — see `docs/IMPLEMENTATION_ROADMAP.md` for the exact
residual scope (generic machine, Koya limits, exotic STD, team).
