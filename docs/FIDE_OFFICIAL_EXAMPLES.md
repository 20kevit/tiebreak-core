# FIDE official examples (corpus candidates)

Every example below is PRIMARY (official FIDE). Status = corpus state
in `tests/corpus/`. "Hand-computed" = derived independently of this
library and recorded in case `notes`.

## C.07-2026 annex (Arbiter Manual 2026, pp.258–261)

| Example | Article | Input (summary) | Calculation | Expected | Status / test path |
|---|---|---|---|---|---|
| Laxman (SOA GM 2024) | §§8.1/9.1/14.1.1/16 | 7.0/10, R4 withdrawal (VUR) | BH 50+7=57 (2024) / 50+5=55 (2026 cap 16.4.2); C1 cut 7.0→50 / cut 5.0→50; SB 37.25 both | BH 57/55, C1 50/50, SB 37.25 | VERIFIED (`LAXMAN-2024…` + `LAXMAN-2026…`, 0.7.0) |
| Ex01 (forfeit win R7) | §§8.1/16.3–16.4 | 7.0/9, sched-opp adj 5.5 | dummy 7.0 (2024) / 5.5 (2026 16.4.1) | BH 51 / 49.5 | VERIFIED + VERIFIED (0.7.0) |
| Ex02 (R1 bye) | §16.4.2 | 4.0/9, cap 4.5 no-op | dummy = own 4.0 both | BH 4.0 both | docs-only (no-op; note the "maximum" wording slip) |
| Ex03 (forfeit loss + withdrawal) | §§8.1/16.4 | 6.5/10 | dummies 6.5+6.5 (2024) / 6.5+5.0 (2026) | BH 64.5 / 63 | VERIFIED + VERIFIED (0.7.0) |
| Ex04 (R1 forfeit win, opp excluded) | §§8.1/16.4.1 | 9.5/10, sched adj 4.5 | dummy 9.5 (2024) / 4.5 (2026) | BH 74 / 69 | VERIFIED + VERIFIED (0.7.0) |
| Ex05 (forfeit win, opp unpaired R6) | §§8.1/16.4.1 | ambiguous ZPB/HPB/FPB | officially unresolved | — | docs-only (ambiguity registered) |
| Ex06 = TEC Ex06 | §§8.1/16.5.1 | #4 3.5/5, R2 HPB (VUR) | cut VUR dummy → 11.5 | BH-C1 11.5 | VERIFIED + VERIFIED (0.7.0; "2.5" vestige noted) |

## TEC Exercises V01-1 (2024-04-16, C.07-2023 basis)

Fully-played BH(#2) = 1.0+1.5+3.5+3.5+3.5 = **13.0**; BH-C1(#4) =
3.5+3.5+3.0+1.5 = **11.5** (FIDE_SOURCES item 4, pre-existing
VERIFIED); AOB / Fore-BH / SB (Swiss + RR) / Koya / ARO / TPR /
APRO / PTP / DE (Swiss + RR) / WIN-WON / BPG-BWG / GE / PS chapters;
Swiss-team MPvGP/BH/ESB/EDE/BC/TBR/BBE/SSSC chapters (team → deferred,
not yet corpus). Remaining chapters are corpus candidates for the
implementation phase (each needs input reconstruction + hand
computation; Art-16 structure unchanged 2023→2026 so chapters stay
valid modulo the 2026 caps).

## Rating-regulations tables (§§8.1a/8.1b)

101-entry p→dp + 51-band D→PD, extracted verbatim, programmatically
verified (101/101, gapless 0–735, dp symmetry); byte-identical
2022→2024. In-code data + `test_ratings.py` + corpus
`fide2024_ratings.json` (VERIFIED).

## C.04 / TRF26 / TEC-manual material

No worked tie-break numbers (pairing examples only) — not corpus;
TRF26 801/802 records are interop fixtures (see TRF26 doc), usable as
differential inputs once a TRF reader exists consumer-side.

## Searched, none found (recorded negatives)

Pre-2023 worked examples beyond the 2022 text; FIDE
certification suites beyond the 50k-RTG TAPC protocol (no fixed
expected-output files published; approval is differential, not
golden). (Correction 2026-10-03: ETT26 DOES exist — it is the C.02.03
Annex C tournament-type code table for TRF field 192, not test
material. See the TEC-requirements doc.)

## Tournament-specific systems (C.07 §4.1 self-defined lists — OTHER_ usage)

Primary event regulations regularly define their own sequences from C.07
codes or bespoke formulas. These are CONSUMER_OWNED (organiser lists,
`OTHER_*` descriptors in TRF 202/212), never core requirements — but
they are the correct differential-test material and the proof that the
`OTHER_` mechanism matters:

- **Olympiad 2026 Main Competition** (`handbook.fide.com/files/handbook/Olympiad2026MainCompetition.pdf`,
  retrieved as indexed text 2026-10-03): team TB1 = Σ IS(10) over the 10 best
  opponents (PAB round excluded, else lowest-MP opponent dropped; ties for
  lowest → drop lowest ISi), ISi = GPi × FMPi (Olympiad-SB variant with a
  10-opponent cut); TB2 = GP; TB3 = Σ MP of 10 opponents minus lowest;
  unbroken ties stand (share top rank of the set). Combined classification
  TB1–TB4 (sums of places/MP/TB1–TB3 across sections). Board prizes by TPR,
  TB1 = games played, TB2 = lots. Unplayed-match arithmetic: unpaired (non-PAB)
  rounds score 1 MP for tie-break purposes; GP(uw)=4 / GP(ul)=0;
  FMP(uw)=FMP+UR, FMP(uwx)=CMP+UR (opponent plays no further),
  FMP(ul)=FMP+UR; IS(uw)=GP(uw)×FMP(uw) etc. (UR = unpaired rounds excl. PAB).
  Status: docs-only differential reference (team + bespoke; NOT corpus).
