# Implementation roadmap (requirements matrix + 1.0 + uncertainties)

## Requirements matrix

Scope note: `F-*` rows are fide-2024 scope (frozen, VERIFIED).
Every 2026 counterpart is an `N-*` row below with its own status
(IMPLEMENTED, SPECIFIED, or DEFERRED with rationale). Per-ruleset
states for each criterion: `FIDE_COMPLETE_REQUIREMENTS_MATRIX.md`.

| ID | Feature | FIDE source | Ruleset | Status | Inputs | Deps | Tests | Priority |
|---|---|---|---|---|---|---|---|---|
| F-BH | BH + C1/C2/M1/M2 | §§8.1, 14.1–14.4, 16 | fide-2024 | IMPLEMENTED | games+kinds+total | R-ADJ/R-DUMMY24/R-VURCUT | corpus VERIFIED | — |
| F-SB | SB + SB-C1 | §§9.1, 14.1.1.d, 16 | fide-2024 | IMPLEMENTED | same | same | corpus VERIFIED | — |
| F-PS | PS + PS-C1 | §§7.5, 14.1.1.c | fide-2024 | IMPLEMENTED | rounds+scores | — | corpus VERIFIED | — |
| F-TYPEB | WIN/WON/BPG/BWG/REP | §§7.1–7.4, 7.6 | fide-2024 | IMPLEMENTED | games+kinds | OTB filter | unit | — |
| F-ARO | ARO + ARO-C1 | §§10.1, 14.1.1.b | fide-2024 | IMPLEMENTED | OTB ratings | half-up | unit | — |
| F-AOB/FB | AOB + Fore BH | §§8.2–8.3, 16 | fide-2024 | IMPLEMENTED | + final-round pairing | FB projection | corpus VERIFIED | — |
| F-KOYA | Koya (max-possible threshold) | §9.2 | fide-2024 | IMPLEMENTED | total_rounds | raw points | unit | — |
| F-RATE | TPR/PTP/APRO/APPO | §§10.2–10.5 + RR 8.1a/b | fide-2024 | IMPLEMENTED | OTB ratings+scores | tables | corpus VERIFIED | — |
| F-DE | DE group stage 6.1–6.3 | §6 | fide-2024 | IMPLEMENTED | mutual games | mini-table | corpus VERIFIED | — |
| F-ART16 | Categories/adjusted/dummy/cuts | §§15.3, 16 | fide-2024 | IMPLEMENTED | kinds | classify() | corpus VERIFIED | — |
| N-DUMMYCAP | §16.4.1/16.4.2 caps | §16.4 (2026) | fide-2026 | IMPLEMENTED (F26-1) | sched-opp adj | F-ART16 | 5 VERIFIED corpus | **P0** |
| N-RR15.2 | RR forfeit carve-out | §15.2 (2026) | fide-2026 | IMPLEMENTED (F26-1) | Swiss/RR mode flag | mode input | unit | P1 |
| N-STD | Standard Points | §7.7 | fide-2026 | IMPLEMENTED standard scope (F26-2c; explicit `opponent_score` or 1-½-0 complement) / SPECIFIED exotic tables (U6 blocks) | sched-opp round scores + scoring table | model ext (optional field landed) | unit | P1 |
| N-TPN | Pairing-number order | §7.8 | fide-2026 | IMPLEMENTED (F26-1, ascending terminal) | pairing numbers | ranking key | unit | P2 |
| N-RTNG | Rating order | §10.6 | fide-2026 | IMPLEMENTED (F26-1, descending terminal) | rating (have) | ranking key | unit | P2 |
| N-PFLAG | Forfeit-inclusion opt-in (/P) | §6.1.1/MTB26 | fide-2026 | IMPLEMENTED (F26-1) | forfeits_as_played flag | BH/SB/FB/Koya/DE scope | unit | P1 |
| N-AOBFB | AOB over Fore BH | §8.2 (2026) | fide-2026 | IMPLEMENTED (F26-2a, additive id `aob_fb`) | FB values | F-AOB/FB | unit | P2 |
| N-C2COMBO | SB-C2/ARO-C2/FB-C1/FB-C2 + FB-M1/M2/ARO-M1/M2 | §§14.1–14.4 | fide-2026 | IMPLEMENTED (F26-2b + hardening: SB-C2 = reapplied C1-cut, documented; PS-C2 declined — no FIDE semantics) | cut helpers | F26-1 cuts | unit + differential | P1 |
| N-RRBAN | BH round-robin ban | Art 8 note | fide-2026 | SPECIFIED | coverage detect | docs/warn | docs | P2 |
| N-KOYALIM | Koya limit ±½ | §14.5 | fide-2024 + fide-2026 | IMPLEMENTED (`koya_limit` offset; echecs-differentially validated) | param | F-KOYA | unit + differential | P1 |
| N-OPT16.6 | Local Art-16 overrides | §16.6 | future | DEFERRED | competition regs | — | — | P3 |
| X-TEAM | MP/GP/BC/TBR/BBE/ESB/EDE/SSSC | §§11–13 | — | IMPLEMENTED (1.1.0 `tiebreak_core.team`; definition-derived tests) | TeamMatch domain | team.py | unit+property | done |
| X-PAIR | C.04 opposition eval | C.04 §§1.7–1.8 | — | CONSUMER_OWNED | snapshots | pairing-core | — | — |
| X-NORMTPR | Title-norm performance | B.01 | — | OUT_OF_SCOPE | floors/mixes | never share | warning | — |
| X-LEGACY | buchholz_sum/arpo/stub-DE | — | legacy-0.1.0 | IMPLEMENTED (frozen) | — | — | goldens | — |

## Order (dependency, not convenience)

1. `fide-2026` skeleton (specified→implemented flag, Swiss/RR mode
   input, TPN/RTNG terminal keys) + N-DUMMYCAP + N-RR15.2 + N-PFLAG
   (/P forfeit-inclusion flag) + corpus activation
   (5 PENDING unplayed shells + 4 PENDING pending.json shells →
   VERIFIED). This is the P0 2026 core: BH/SB parity
   with the Manual's NEW columns. DONE in 0.7.0 (Phase F26-1).
2. N-RR15.2 (RR mode: forfeit scope in §10/Type-B sets) + D9 contract
   wording in adapter docs.
3. N-STD (model: scheduled-opp scores + scoring table) behind new
   input fields; N-AOBFB as additive id; N-RRBAN warning.
4. Property/perf tests per conformance plan; consumer per-tournament
   `fide-2026` opt-in; 1.0.

## 1.0 definition

`fide-2026` implemented (N-DUMMYCAP + N-RR15.2 + TPN/RTNG/STD
implemented; Koya limits implemented) + zero PENDING corpus cases
(all VERIFIED) + perf budgets met + consumer per-tournament
adoption (chess-manager side, outside this repo). Team systems and
16.6 overrides are explicitly NOT 1.0 blockers (documented
rationale above).

## Uncertainty register (classified: ID / Question / Evidence / Impact / Blocking / Owner / Action)

| ID | Question | Evidence | Impact | Blocking | Owner | Action |
|---|---|---|---|---|---|---|
| U1 | §16 header "(Until 28th February 2026)" vs March-2026 body | Manual p.257 vs live Handbook title (no qualifier) | none on calculations (body + examples unambiguous) | NON-BLOCKING | core docs | re-verify on Handbook reachability |
| U2 | 02/02/2026 instrument number/URL | no indexed doc.fide.com record found | none (dates VERIFIED independently) | NON-BLOCKING | docs | record when published |
| U3 | Manual Ex02 "maximum" vs cap wording | numbers fit cap reading | none | NON-BLOCKING | corpus notes | none (recorded) |
| U4 | Manual Ex05 unpaired-round scoring genuinely ambiguous | official text punts ("might be ZPB/HPB/FPB") | Ex05 stays docs-only | NON-BLOCKING for F26-1 | FIDE (class-c clarification) | none in-repo |
| U5 | Ex06 "2.5" vestige | totals coincide at 11.5 | none | NON-BLOCKING | corpus notes | none (recorded) |
| U6 | STD exotic-table mapping | unspecified by FIDE | standard-scoring STD implemented (F26-2c) with explicit-`opponent_score` organizer contract; exotic own-score values (e.g. 3.0) still outside the core score model | BLOCKS exotic STD only, not standard | consumer contract | score-table model extension if a consumer requires exotic scoring |
| U7 | SSSC normaliser edges | Handbook text only | team module only | NON-BLOCKING (team deferred) | future team module | implement from text if built |
| U8 | WRBC fine print | downloads failed; snippets convergent | none (standard scoring, C.07-referenced) | NON-BLOCKING | docs | none |
| U9 | ETT26 Handbook-PDF direct bytes | hosts unreachable; content verified via index + TEC table | version labels (DUTCH_2025 vs 2026 cutover) recorded; Handbook governs | NON-BLOCKING | docs | re-fetch on reachability |
| U10 | THP VCL final text; PIWE chapter | "subject to final VCL"; Manual only outlines | approval-side only; zero core impact | NON-BLOCKING | vendor/FIDE | track per Acceptance Cycle |
| U11 | EX04 Amit R2–R10 representation (exclusion vs bye-recorded) | Manual NEW BH=69 requires Amit adjusted 4.5 = 0.0+9×0.5, i.e. R2–R10 recorded as trailing zero-byes (16.2.5→draws), mirroring the EX01 Leo stub | corpus encodes trailing zero-byes with an explicit INPUT NOTE; engine implements the recorded-rounds reading (§§16.1–16.3) | RESOLVED (hardening audit): the Manual's Ex04 prose states the arithmetic outright — "0 (scheduled opponent's score) plus ½ point for every remaining unpaired round … 0 + (½×9) = 4.5" — confirming the encoded representation reproduces official arithmetic exactly; the absent-reading alternative is refuted by the printed text | — | closed |

## Recommended next autonomous phase

Phase F26-1: implement N-DUMMYCAP + Swiss/RR mode (+ ETT192-derived regime flag) + TPN/RTNG keys,
activate the PENDING shells, extend property/perf tests, cut the next
minor release with `fide-2026` status=implemented (Swiss scope).
DONE in 0.7.0 — evidence, ownership, API impact, and tests all landed;
no further research required first. F26-2 (N-STD standard scope +
SB-C2/ARO-C2/FB-C1/FB-C2 + AOB/FB) DONE in 0.8.0. Remaining
Remaining SPECIFIED surface: exotic STD without explicit scores
(U6, typed error), Art.16.6 competition-specific engine behavior
beyond the `Article16Policy` value object. DONE in 1.1.0: generic
/Cn//Mn machine, Koya limits (already landed pre-1.0; now also team
KS + /L descriptors), team module, /R reversal, PS/Cn machine,
policy/scoring models.
