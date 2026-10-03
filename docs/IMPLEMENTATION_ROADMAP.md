# Implementation roadmap (requirements matrix + 1.0 + uncertainties)

## Requirements matrix

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
| N-DUMMYCAP | §16.4.1/16.4.2 caps | §16.4 (2026) | fide-2026 | SPECIFIED | sched-opp adj | F-ART16 | 6 PENDING shells | **P0** |
| N-RR15.2 | RR forfeit carve-out | §15.2 (2026) | fide-2026 | SPECIFIED | Swiss/RR mode flag | mode input | PENDING | P1 |
| N-STD | Standard Points | §7.7 | fide-2026 | SPECIFIED | sched-opp round scores + scoring table | model ext | PENDING | P1 |
| N-TPN | Pairing-number order | §7.8 | fide-2026 | SPECIFIED | pairing numbers | ranking key | unit | P2 |
| N-RTNG | Rating order | §10.6 | fide-2026 | SPECIFIED | rating (have) | ranking key | unit | P2 |
| N-RRBAN | BH round-robin ban | Art 8 note | fide-2026 | SPECIFIED | coverage detect | docs/warn | docs | P2 |
| N-AOBFB | AOB over Fore BH | §8.2 (2026) | fide-2026 | SPECIFIED | FB values | F-AOB/FB | unit | P2 |
| N-KOYALIM | Koya limit ±½ | §14.5 | future | DEFERRED | param | F-KOYA | — | P3 |
| N-OPT16.6 | Local Art-16 overrides | §16.6 | future | DEFERRED | competition regs | — | — | P3 |
| X-TEAM | MP/GP/BC/TBR/BBE/ESB/EDE/SSSC | §§11–13 | — | OUT_OF_SCOPE | TeamMatch domain | new module | — | on demand |
| X-PAIR | C.04 opposition eval | C.04 §§1.7–1.8 | — | CONSUMER_OWNED | snapshots | pairing-core | — | — |
| X-NORMTPR | Title-norm performance | B.01 | — | OUT_OF_SCOPE | floors/mixes | never share | warning | — |
| X-LEGACY | buchholz_sum/arpo/stub-DE | — | legacy-0.1.0 | IMPLEMENTED (frozen) | — | — | goldens | — |

## Order (dependency, not convenience)

1. `fide-2026` skeleton (reserved→implemented flag, Swiss/RR mode
   input, TPN/RTNG terminal keys) + N-DUMMYCAP + corpus activation
   (6 PENDING → VERIFIED). This is the P0 2026 core: BH/SB parity
   with the Manual's NEW columns.
2. N-RR15.2 (RR mode: forfeit scope in §10/Type-B sets) + D9 contract
   wording in adapter docs.
3. N-STD (model: scheduled-opp scores + scoring table) behind new
   input fields; N-AOBFB as additive id; N-RRBAN warning.
4. Property/perf tests per conformance plan; consumer per-tournament
   `fide-2026` opt-in; 1.0.

## 1.0 definition

`fide-2026` implemented (N-DUMMYCAP + N-RR15.2 + TPN/RTNG/STD
specified-or-implemented per consumer need) + all PENDING corpus
green + chess-manager per-tournament adoption + perf budgets met.
Team systems, Koya-limit machinery, and 16.6 overrides are explicitly
NOT 1.0 blockers (documented rationale above).

## Uncertainty register

1. §16 header "(Until 28th February 2026)" contradicts its March-2026
   body — treated as stale editorial; re-verify vs live Handbook.
2. 02/02/2026 approving instrument number/URL — UNVERIFIED (dates
   themselves are RETRIEVED).
3. Manual Ex02 "maximum between own score and 50%" vs cap semantics —
   example wording slip; numbers consistent with cap reading.
4. Manual Ex05 acknowledges under-specified unpaired-round scoring —
   genuinely ambiguous; needs FIDE clarification, stays docs-only.
5. Ex06 "2.5" intermediate vs 2024 dummy 3.5 — draft vestige; totals
   coincide at 11.5 either way.
6. STD unplayed-vs-draw-value mapping for exotic scoring tables —
   unspecified by FIDE; needs organiser regulation input.
7. SSSC normaliser edge cases (truncation, custom values) — implement
   from Handbook text if a team module is ever built.
8. WRBC PDF fine print — MEDIUM confidence (downloads failed);
   substance convergent across snippets; no tiebreak-core impact
   (standard scoring, C.07-referenced).

## Recommended next autonomous phase

Phase F26-1: implement N-DUMMYCAP + Swiss/RR mode + TPN/RTNG keys,
activate the 6 PENDING shells, extend property/perf tests, cut
release 0.4.0 with `fide-2026` status=implemented (Swiss scope).
Evidence, ownership, API impact, and tests are all settled above —
no further research required first.
