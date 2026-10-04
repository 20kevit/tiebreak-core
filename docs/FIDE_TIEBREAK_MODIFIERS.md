# FIDE tie-break modifiers (complete inventory)

Normative base: C.07 Article 14 + §§6.1.1/7.8/10.6/13.3.2.
Descriptor layer: MTB26 (`FIDE_MTB26_CATALOG.md`). MTB26 codes using a
modifier are mandatory for approval once the base exists; generic
`/Cn /Mn /Lx /Kx` instantiations ("any reasonable value") are
machine-readable combinations, not separately named FIDE criteria.

## C.07 modifiers

| Modifier | C.07 | Meaning | Named FIDE combos | Status |
|---|---|---|---|---|
| Cut-1 | §14.1.1 | drop least-significant value (+§16.5 VUR rule) | BH-C1, ARO-C1, PS-C1, SB-C1 (higher-of), FB-C1, ESB-C1 (§14.1.2) | IMPLEMENTED (individual named + team ESB-C1) |
| Cut-2 | §14.2 | drop two least-significant | BH-C2, SB-C2, ARO-C2, FB-C2 | IMPLEMENTED (individual named + team ESB-C2 reapplied; SB-C2 = reapplied C1-cut, documented) |
| PS-C2 | MTB26 machine (generalised §14.1.1.c) | exclude cumulative scores after rounds 1–2 | PS/C2 | IMPLEMENTED (1.1.0 generic PS/Cn round-exclusion; NOT a C.07-named combo — never present it as one) |
| Cut-n (generic) | MTB26 `/Cn` | drop n least-significant | codes BH/Cn etc. | IMPLEMENTED (1.1.0 `tiebreak_core.modifiers`; BH/SB/ARO/FB + team BH refs; n=1/2 delegate to named ids) |
| Median-1 | §14.3 | least then most, in that order | BH-M1, FB-M1, ARO-M1 | IMPLEMENTED |
| Median-2 | §14.4 | two least then two most | BH-M2, FB-M2, ARO-M2 | IMPLEMENTED |
| Median-n (generic, n≥3) | MTB26 `/Mn` | drop n least + n most | BH/Mn… | IMPLEMENTED (1.1.0; BH/ARO/FB + team BH refs) |
| Limit | §14.5 | Koya 50% threshold ±½ steps | KS/L±n | IMPLEMENTED (`koya_limit` offset, half-point steps; echecs-differentially validated; team KS:MP/:GP too) |
| Forfeit inclusion | §6.1.1 (DE), MTB26 `/P` | forfeits count as played vs scheduled opp | DE/P, SB/P, BH/P, FB/P, EDE/P… | IMPLEMENTED (fide-2026 `forfeits_as_played` flag + `/P` descriptors; BH/SB/FB/Koya/DE scope; Type-B + ratings unaffected) |
| Fore variant | §8.3, MTB26 `/F` | BH computed on final-round draws | AOB/F, FB base/C1/C2, SSSC/F… | IMPLEMENTED (FB base/C1/C2 + AOB/FB + team SSSC/F + team FB:MP/:GP) |
| Reverse order | §§7.8/10.6, MTB26 `/R` | descending pairing no. / ascending rating | TPN/R, RTNG/R | IMPLEMENTED (1.1.0 `rank_descriptors`) |
| Team score ref | §13 blanket, `:` | :MP / :GP reference | WIN:MP, BH:GP/C1… | IMPLEMENTED (1.1.0 team module; bare SB:MP-style codes stay rejected — team SB is the ESB family) |
| SSSC divisor | §13.4.2, `/Kx` | custom normaliser | SSSC/Kx… | IMPLEMENTED (1.1.0 team module) |
| EDE+knockout chains | §13.3.2 (2026) | EDEBT/EDEBB/EDET/EDEB | team codes | IMPLEMENTED (1.1.0 team module; pair-only) |
| Organiser-defined | §4.1, `OTHER_*` | self-defined, TRF 202/212 | any | CONSUMER_OWNED (pass-through; core must not reject unknown `OTHER_` descriptors at parse level — strict unknown-criterion errors apply only to calculation requests) |

## Cut/median application order (normative)

Median cuts apply least-first (§§14.3–14.4 "in that order"); every
least-cut is subject to the §16.5 VUR exception, reapplied per cut
(§16.5.2); never cut the last remaining element (documented edge
guard, not a FIDE rule — FIDE assumes full Swiss coverage).

## Explicitly NOT FIDE modifiers (software convention)

`progressiveCut2` as "two lowest cumulative totals", ARO-M1/M2 beyond
MTB26 machine readings, percentage-normalised WON/BPG/BWG (rejected
by TEC 2025, see history doc), virtual-opponent toggles (abolished
2023). Never present these as FIDE-defined.
