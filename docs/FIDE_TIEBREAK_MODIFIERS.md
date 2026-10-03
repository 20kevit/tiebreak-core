# FIDE tie-break modifiers (complete inventory)

Normative base: C.07 Article 14 + §§6.1.1/7.8/10.6/13.3.2.
Descriptor layer: MTB26 (`FIDE_MTB26_CATALOG.md`). MTB26 codes using a
modifier are mandatory for approval once the base exists; generic
`/Cn /Mn /Lx /Kx` instantiations ("any reasonable value") are
machine-readable combinations, not separately named FIDE criteria.

## C.07 modifiers

| Modifier | C.07 | Meaning | Named FIDE combos | Status |
|---|---|---|---|---|
| Cut-1 | §14.1.1 | drop least-significant value (+§16.5 VUR rule) | BH-C1, ARO-C1, PS-C1, SB-C1 (higher-of), ESB-C1 (§14.1.2) | IMPLEMENTED (individual named) |
| Cut-2 | §14.2 | drop two least-significant | BH-C2 | IMPLEMENTED; other C2 SPECIFIED |
| Cut-n (generic) | MTB26 `/Cn` | drop n least-significant | codes BH/Cn etc. | SPECIFIED (machine) |
| Median-1 | §14.3 | least then most, in that order | BH-M1 | IMPLEMENTED |
| Median-2 | §14.4 | two least then two most | BH-M2 | IMPLEMENTED |
| Median-n (generic) | MTB26 `/Mn` | — | ARO/M1/M2, BH/Mn… | SPECIFIED (machine) |
| Limit | §14.5 | Koya 50% threshold ±½ steps | KS/L±n | SPECIFIED |
| Forfeit inclusion | §6.1.1 (DE), MTB26 `/P` | forfeits count as played vs scheduled opp | DE/P, SB/P, BH/P, FB/P, EDE/P… | SPECIFIED (flag input) |
| Fore variant | §8.3, MTB26 `/F` | BH computed on final-round draws | AOB/F, FB base, SSSC/F… | IMPLEMENTED (FB); combos SPECIFIED |
| Reverse order | §§7.8/10.6, MTB26 `/R` | descending pairing no. / ascending rating | TPN/R, RTNG/R | SPECIFIED |
| Team score ref | §13 blanket, `:` | :MP / :GP reference | WIN:MP, BH:GP/C1… | OUT_OF_SCOPE (team) |
| SSSC divisor | §13.4.2, `/Kx` | custom normaliser | SSSC/Kx… | OUT_OF_SCOPE |
| EDE+knockout chains | §13.3.2 (2026) | EDEBT/EDEBB/EDET/EDEB | team codes | OUT_OF_SCOPE |
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
