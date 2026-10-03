# FIDE complete requirements matrix

Formulas live in `FIDE_CRITERIA_CATALOG.md` (referenced, not
duplicated). Modifier machine: `FIDE_TIEBREAK_MODIFIERS.md`. MTB26
codes: `FIDE_MTB26_CATALOG.md`. Statuses: IMPLEMENTED /
PARTIALLY_IMPLEMENTED / SPECIFIED / VERIFIED / PENDING_SOURCE /
UNVERIFIED / DEFERRED / CONSUMER_OWNED / OUT_OF_SCOPE.

## Individual criteria (Swiss)

| Req | Source/Art | Criterion/Modifier | Ruleset | Type | Inputs | Deps | Formula → | Example | Test | Impl | Owner | Pri |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q-BH | C.07 §8.1 | BH | 2024/26 | Swiss | opp finals, kinds | 16.3/16.4 | catalog §BH | Manual Laxman | VERIFIED corpus | IMPLEMENTED | core | — |
| Q-BHC1 | §14.1.1.a+16.5 | BH-C1 | 2024/26 | Swiss | +VUR flags | VUR-cut | catalog | Laxman/Ex06 | VERIFIED | IMPLEMENTED | core | — |
| Q-BHC2 | §14.2+16.5.2 | BH-C2 | 2024/26 | Swiss | same | reapply | catalog | — | unit | IMPLEMENTED | core | — |
| Q-BHM | §§14.3–14.4 | BH-M1/M2 | 2024/26 | Swiss | same | order | catalog | — | unit | IMPLEMENTED | core | — |
| Q-BHGEN | MTB26 /Cn /Mn | generic cuts/medians | 2026 | Swiss | n | machine | modifiers | — | — | SPECIFIED | core | P2 |
| Q-AOB | §8.2 | AOB (+/F) | 2024/26 | Swiss | opp BH | FB proj | catalog | TEC AOB | unit | IMPLEMENTED (base) | core | — |
| Q-FB | §8.3 | FB (+cuts/P) | 2024/26 | Swiss | final pairing | draws | catalog | TEC FB | VERIFIED | IMPLEMENTED (base) | core | — |
| Q-SB | §9.1 | SB | 2024/26 | Swiss | opp finals × scores | 16.3/16.4 | catalog | Laxman 37.25 | VERIFIED | IMPLEMENTED | core | — |
| Q-SBC1 | §14.1.1.d+16.5 | SB-C1 (+/C2 /P) | 2024/26 | Swiss | +VUR | higher-of | catalog | — | unit | IMPLEMENTED (C1) | core | — |
| Q-PS | §7.5 | PS (+:MP/:GP /C1 /C2) | 2024/26 | Swiss | round scores | gap-fill | catalog | — | unit | IMPLEMENTED (PS, PS-C1) | core | — |
| Q-KOYA | §9.2+14.5 | KS (+:MP/:GP /Lx) | 2024/26 | RR/Swiss-arith | total=max | raw pts | catalog | TEC Koya | unit | IMPLEMENTED (base) | core | — |
| Q-TYPEB | §§7.1–7.4,7.6 | WIN/WON/BPG/BWG/REP | 2024/26 | Swiss | games+kinds | OTB | catalog | TEC ch.7 | unit | IMPLEMENTED | core | — |
| Q-STD | §7.7 | STD | 2026 | any scoring | sched-opp scores + 013 table | draw-value | catalog | — | — | SPECIFIED | core | P1 |
| Q-TPN | §7.8 | TPN/R | 2026 | any | pairing nos | order | catalog | — | — | SPECIFIED | core+consumer | P2 |
| Q-ARO | §10.1 | ARO (+/C1/C2/M1/M2) | 2024/26 | Swiss | OTB ratings | half-up | catalog | — | unit | IMPLEMENTED (base+C1) | core | — |
| Q-TPR | §10.2+RR8.1a | TPR | 2024/26 | Swiss | OTB frac | table | catalog | TEC TPR | VERIFIED | IMPLEMENTED | core | — |
| Q-PTP | §10.3+RR8.1b | PTP | 2024/26 | Swiss | OTB scores | full scale | catalog | — | VERIFIED | IMPLEMENTED | core | — |
| Q-APRO | §10.4 | APRO | 2024/26 | Swiss | opp TPR | half-up | catalog | TEC APRO | VERIFIED | IMPLEMENTED | core | — |
| Q-APPO | §10.5 | APPO | 2024/26 | Swiss | opp PTP | half-up | catalog | — | VERIFIED | IMPLEMENTED | core | — |
| Q-RTNG | §10.6 | RTNG/R | 2026 | any | rating | order | catalog | — | — | SPECIFIED | core+consumer | P2 |
| Q-DE | §6.1–6.3 | DE (+/P) | 2024/26 | Swiss/RR | mutual games | mini-table | catalog+ADR-008 | TEC DE | VERIFIED | IMPLEMENTED | core | — |
| Q-ART16 | §§15.3/16 | categories/adj/dummy/cuts | 2024 | Swiss | kinds | classify | data-sem §3 | Manual 01–06 | VERIFIED | IMPLEMENTED | core | — |
| Q-DUMMY26 | §16.4.1–2 | dummy caps | 2026 | Swiss | sched-opp adj | Q-ART16 | diff D13 | Manual NEW | PENDING ×6 | SPECIFIED | core | P0 |
| Q-RR152 | §15.2 | RR forfeit scope | 2026 | RR/pre-paired | mode flag | sets | diff D12 | — | — | SPECIFIED | core | P1 |
| Q-RRBAN | Art-8 note | BH RR ban | 2026 | RR | coverage | warn | diff D7 | — | — | SPECIFIED | core+consumer | P2 |
| Q-FIRSTR | §10 note | first-rating rule | 2026 | any | snapshot | contract | diff D9 | — | contract | IMPLEMENTED-by-construction | consumer | — |
| Q-SEQ | §§4.1–4.2 | ordered lists + subgroups → lots | all | any | descriptors | ranking | arch-gap §26 | — | ranking tests | IMPLEMENTED+CONSUMER_OWNED (selection) | shared | — |

## Team criteria (all OUT_OF_SCOPE; team-module on demand)

| Req | Art | Code | Inputs | Status |
|---|---|---|---|---|
| T-MPGP | §11 | MP/GP primitives | match scores | OUT_OF_SCOPE |
| T-KO | §12 | BC/TBR/BBE (+forfeit/PAB rules) | board GP matrix | OUT_OF_SCOPE |
| T-ESB | §13.2+14.1.2 | EMMSB/EMGSB/EGMSB/EGGSB /C1/C2/P | opp MP/GP × scored | OUT_OF_SCOPE |
| T-EDE | §13.3+13.3.2 | EDE /P, EDEBT/EDEBB/EDET/EDEB | primary→secondary, KO chains | OUT_OF_SCOPE |
| T-SSSC | §13.4 | SSSC /F/P/Kx | secondary + BH ÷ normaliser | OUT_OF_SCOPE |
| T-MPVGP | §13.1 | MPvGP | other score | OUT_OF_SCOPE |
| T-IND | §13 blanket | individual codes :MP/:GP | TeamMatch | OUT_OF_SCOPE |

## Regimes, interchange, approval

| Req | Source | Behavior | Status | Owner |
|---|---|---|---|---|
| G-RR | §§9.2/15.2/Art-8-note | RR regime (Koya home, forfeit scope, BH ban) | SPECIFIED | core (mode flag) |
| G-KO | Art 3 + §12/13.3.2 | play-offs + team-KO chains | OUT_OF_SCOPE / CONSUMER_OWNED (play-off format) | consumer |
| G-PAIR | C.04 §§1.7–1.8 | pairing-time BH/SB/TPN | CONSUMER_OWNED (pairing-core) | pairing-core |
| I-TRF | TRF26 202/212/192/013/240/320/801/802 | descriptor + data interchange | CONSUMER_OWNED (parser) + core consumes ids | consumer |
| I-PTC/RTG | TEC Manual §3.9.4 | 50k differential verification | CONSUMER_OWNED (THP vendor) | vendor |
| I-TAPC | C.02.01 + TEC Manual | VCL/SDPC/TAPC/FEAP, cycles | CONSUMER_OWNED | vendor+FIDE |
| I-ETT | — (negative: no such format) | PTC+RTG+TRF are the instruments | documented absence | — |
| X-LEGACY | — | buchholz_sum/arpo/stub-DE frozen | IMPLEMENTED (frozen) | core |
| X-NORMTPR | B.01 | norm performance (floors/1400/35%) | OUT_OF_SCOPE + warning | — |

UNVERIFIED rows: none (every behavior above was read in a primary
text; the only UNVERIFIED items in-repo are the 02/02/2026 instrument
number and WRBC fine print — neither affects a requirement row).
PENDING_SOURCE rows: none.

## Acronym ↔ code-id ↔ requirement crosswalk (single source of truth)

| Acronym (C.07/MTB26) | tiebreak-core code id | Requirement row |
|---|---|---|
| BH / BH-C1 / BH-C2 / BH-M1 / BH-M2 | `buchholz` / `buchholz_cut1` / `buchholz_cut2` / `median_buchholz` / `median_buchholz_2` | Q-BH / Q-BHC1 / Q-BHC2 / Q-BHM |
| AOB / FB | `aob` / `fore_buchholz` | Q-AOB / Q-FB |
| SB / SB-C1 | `sonneborn_berger` / `sonneborn_berger_cut1` | Q-SB / Q-SBC1 |
| PS / PS-C1 | `progressive` / `progressive_cut1` | Q-PS |
| KS | `koya` | Q-KOYA |
| WIN / WON / BPG / BWG / REP | `wins` / `won` / `games_black` / `wins_black` / `rounds_elected` | Q-TYPEB |
| STD / TPN / RTNG | `std` / `tpn` / `rtng` (reserved ids) | Q-STD / Q-TPN / Q-RTNG |
| ARO / ARO-C1 | `aro` / `aro_cut1` | Q-ARO |
| TPR / PTP / APRO / APPO | `tpr` / `ptp` / `apro` / `appo` | Q-TPR / Q-PTP / Q-APRO / Q-APPO |
| DE (group stage; no scalar) | positional stage (scalar `direct_encounter` refused under fide-2024) | Q-DE |
| MPvGP / EMMSB / EMGSB / EGMSB / EGGSB / EDE(+chains) / SSSC / BC / TBR / BBE | team module (no ids minted) | T-* |
| buchholz_sum / arpo (non-FIDE / legacy) | frozen legacy ids | X-LEGACY |
