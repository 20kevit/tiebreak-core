# FIDE complete requirements matrix

Formulas live in `FIDE_CRITERIA_CATALOG.md` (referenced, not
duplicated). Modifier machine: `FIDE_TIEBREAK_MODIFIERS.md`. MTB26
codes: `FIDE_MTB26_CATALOG.md`. Statuses: IMPLEMENTED /
PARTIALLY_IMPLEMENTED / SPECIFIED / VERIFIED / PENDING_SOURCE /
UNVERIFIED / DEFERRED / CONSUMER_OWNED / OUT_OF_SCOPE.

## Individual criteria (Swiss)

| Req | Source/Art | Criterion/Modifier | Ruleset | Type | Inputs | Deps | Formula → | Example | Test | Impl | Owner | Pri |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q-BH | C.07 §8.1 | BH | 2024 + 2026 | Swiss | opp finals, kinds | 16.3/16.4 | catalog §BH | Manual Laxman | VERIFIED corpus (2024 + 2026) | 2024: IMPLEMENTED · 2026: IMPLEMENTED (caps, F26-1) | core | P0 |
| Q-BHC1 | §14.1.1.a+16.5 | BH-C1 (BH/C1) | 2024 + 2026 | Swiss | +VUR flags | VUR-cut | catalog | Laxman/Ex06 | VERIFIED (2024 + 2026) | 2024: IMPLEMENTED · 2026: IMPLEMENTED (caps, F26-1) | core | P0 |
| Q-BHC2 | §14.2+16.5.2 | BH-C2 (BH/C2) | 2024 + 2026 | Swiss | same | reapply | catalog | — | unit | 2024: IMPLEMENTED · 2026: IMPLEMENTED (caps, F26-1) | core | P0 |
| Q-BHM | §§14.3–14.4 | BH-M1/M2 (BH/M1/M2) | 2024 + 2026 | Swiss | same | order | catalog | — | unit + VERIFIED (2026 MEDIAN2) | 2024: IMPLEMENTED · 2026: IMPLEMENTED (caps, F26-1) | core | P0 |
| Q-BHGEN | MTB26 /Cn /Mn | generic cuts/medians | 2026 | Swiss | n | machine | modifiers | — | — | SPECIFIED | core | P2 |
| Q-AOB | §8.2 | AOB (+/F) | 2024 + 2026 | Swiss | opp BH | FB proj | catalog | TEC AOB | unit | 2024: IMPLEMENTED (base) · 2026: IMPLEMENTED (base + FB variant, under caps) | core | P1 |
| Q-FB | §8.3 | FB (+cuts/P) | 2024 + 2026 | Swiss | final pairing | draws | catalog | TEC FB | VERIFIED (2024) + unit (2026 caps+/P) | 2024: IMPLEMENTED (base) · 2026: IMPLEMENTED (base + C1/C2/M1/M2, under caps; /P flag) | core | P0 |
| Q-SB | §9.1 | SB | 2024 + 2026 | Swiss | opp finals × scores | 16.3/16.4 | catalog | Laxman 37.25 | VERIFIED (2024 + 2026) | 2024: IMPLEMENTED · 2026: IMPLEMENTED (caps, F26-1) | core | P0 |
| Q-SBC1 | §14.1.1.d+16.5 | SB-C1 (SB/C1; +/C2 /P) | 2024 + 2026 | Swiss | +VUR | higher-of | catalog | — | unit + VERIFIED (2026 SB-C1) | 2024: IMPLEMENTED (C1) · 2026: IMPLEMENTED (C1, under caps; /P flag) | core | P0 |
| Q-SBC2 | §14.2+16.5.2 | SB-C2 (SB/C2) | 2026 | Swiss | +VUR | reapply C1-cut | modifiers | — | unit (F26-2 hand-computed) | IMPLEMENTED (F26-2; reapplied-C1 reading, documented) | core | P1 |
| Q-PS | §7.5 | PS (+:MP/:GP /C1 /C2) | 2024 + 2026 | Swiss | round scores | gap-fill | catalog | — | unit | 2024: IMPLEMENTED (PS, PS-C1) · 2026: IMPLEMENTED (same; no semantic delta) | core | P1 |
| Q-KOYA | §9.2+14.5 | KS (+:MP/:GP /Lx) | 2024 + 2026 | RR/Swiss-arith | total=max | raw pts | catalog | TEC Koya | unit + differential (echecs limits) | 2024: IMPLEMENTED (base + limits) · 2026: IMPLEMENTED (base + RR//P forfeit scope + limits) | core | P1 |
| Q-TYPEB | §§7.1–7.4,7.6 | WIN/WON/BPG/BWG/REP | 2024 + 2026 | Swiss | games+kinds | OTB | catalog | TEC ch.7 | unit | 2024: IMPLEMENTED · 2026: IMPLEMENTED (Swiss + RR-mode §15.2 scope) | core | P1 |
| Q-STD | §7.7 | STD | 2026 | standard scoring | sched-opp round scores (explicit or 1-½-0 complement) + draw value | draw-value | catalog | — | unit (F26-2 hand-computed) | IMPLEMENTED (F26-2; exotic tables BLOCKED U6) | core | P1 |
| Q-TPN | §7.8 | TPN/R | 2026 | any | pairing nos | order | catalog | — | unit (terminal ordering) | IMPLEMENTED (ascending terminal; reverse consumer-side) | core+consumer | P2 |
| Q-ARO | §10.1 | ARO (+/C1/C2/M1/M2) | 2024 + 2026 | Swiss | OTB ratings | half-up | catalog | — | unit | 2024: IMPLEMENTED (base+C1) · 2026: IMPLEMENTED (base+C1+C2+M1+M2) | core | P1 |
| Q-AOBFB | §8.2 (2026) | AOB/FB | 2026 | Swiss | opp FB | FB proj | diff D8 | — | unit (F26-2 hand-computed) | IMPLEMENTED (F26-2, additive id `aob_fb`) | core | P2 |
| Q-TPR | §10.2+RR8.1a | TPR | 2024 + 2026 | Swiss | OTB frac | table | catalog | TEC TPR | VERIFIED (2024) + unit (2026 parity) | 2024: IMPLEMENTED · 2026: IMPLEMENTED (same sets) | core | P1 |
| Q-PTP | §10.3+RR8.1b | PTP | 2024 + 2026 | Swiss | OTB scores | full scale | catalog | — | VERIFIED (2024) + unit (2026 parity) | 2024: IMPLEMENTED · 2026: IMPLEMENTED (same sets) | core | P1 |
| Q-APRO | §10.4 | APRO | 2024 + 2026 | Swiss | opp TPR | half-up | catalog | TEC APRO | VERIFIED (2024) + unit (2026 parity) | 2024: IMPLEMENTED · 2026: IMPLEMENTED (same sets) | core | P1 |
| Q-APPO | §10.5 | APPO | 2024 + 2026 | Swiss | opp PTP | half-up | catalog | — | VERIFIED (2024) + unit (2026 parity) | 2024: IMPLEMENTED · 2026: IMPLEMENTED (same sets) | core | P1 |
| Q-RTNG | §10.6 | RTNG/R | 2026 | any | rating | order | catalog | — | unit (terminal ordering) | IMPLEMENTED (descending terminal; reverse consumer-side) | core+consumer | P2 |
| Q-DE | §6.1–6.3 | DE (+/P) | 2024 + 2026 | Swiss/RR | mutual games | mini-table | catalog+ADR-008 | TEC DE | VERIFIED (2024) + VERIFIED (2026 minitable) | 2024: IMPLEMENTED · 2026: IMPLEMENTED (same §§6.1–6.3; /P flag; RR forfeit scope) | core | P1 |
| Q-ART16 | §§15.3/16 | categories/adj/dummy/cuts | 2024 + 2026 | Swiss | kinds | classify | data-sem §3 | Manual 01–06 | VERIFIED (2024 + 2026) | 2024: IMPLEMENTED · 2026: IMPLEMENTED (caps, F26-1) | core | P0 |
| Q-DUMMY26 | §16.4.1–2 | dummy caps | 2026 | Swiss | sched-opp adj | Q-ART16 | diff D13 | Manual NEW | VERIFIED ×5 (BH 55/49.5/63/69, C1 50/11.5, SB 37.25) | IMPLEMENTED (F26-1) | core | P0 |
| Q-RR152 | §15.2 | RR forfeit scope | 2026 | RR/pre-paired | mode flag | sets | diff D12 | — | unit (RR mode) | IMPLEMENTED (F26-1) | core | P1 |
| Q-RRBAN | Art-8 note | BH RR ban | 2026 | RR | coverage | warn | diff D7 | — | — | SPECIFIED | core+consumer | P2 |
| Q-FIRSTR | §10 note | first-rating rule | 2026 | any | snapshot | contract | diff D9 | — | contract | IMPLEMENTED-by-construction | consumer | — |
| Q-SEQ | §§4.1–4.2 | ordered lists + subgroups → lots | all | any | descriptors | ranking | arch-gap §26 | — | ranking tests | IMPLEMENTED+CONSUMER_OWNED (selection) | shared | — |

## Team criteria (FIDE-defined YES; THP-mandatory YES where MTB26-listed; core implementation NO)

Deferred from the current tiebreak-core scope SOLELY because the current
domain model (`GameRecord`: one player's game) and consumer do not require
them — NOT because they are optional for a complete FIDE-approved THP
(they are mandatory there wherever MTB26 lists them). Required future
domain: TeamMatch (round, opponent team, MP/GP for-against, per-board GP
vector, unplayed/bye flags) in a team module beside — not inside — the core.

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
| G-RR | §§9.2/15.2/Art-8-note | RR regime (Koya home, forfeit scope, BH ban) | PARTIALLY_IMPLEMENTED (mode flag + §15.2 scope live; Art-8 BH ban documented, not enforced) | core (mode flag) |
| G-KO | Art 3 + §12/13.3.2 | play-offs + team-KO chains | OUT_OF_SCOPE / CONSUMER_OWNED (play-off format) | consumer |
| G-PAIR | C.04 §§1.7–1.8 | pairing-time BH/SB/TPN | CONSUMER_OWNED (pairing-core) | pairing-core |
| I-TRF | TRF26 202/212/192/013/240/320/801/802 | descriptor + data interchange | CONSUMER_OWNED (parser) + core consumes ids | consumer |
| I-PTC/RTG | TEC Manual §3.9.4 | 50k differential verification | CONSUMER_OWNED (THP vendor) | vendor |
| I-TAPC | C.02.01 + TEC Manual | VCL/SDPC/TAPC/FEAP, cycles | CONSUMER_OWNED | vendor+FIDE |
| I-ETT | ETT26 (C.02.03 Annex C) | 192 code → format regime (Swiss/RR/team/KO/custom) → §15.2-vs-16/BH-ban/team-code selection | SPECIFIED (mapping table in TEC-requirements doc) | consumer (adapter owns 192 parse + lookup + mode flag; core receives normalized mode) |
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
| STD / TPN / RTNG | `std` / `tpn` / `rtng` (implemented fide-2026 ids; `tpn`/`rtng` terminal stages) | Q-STD / Q-TPN / Q-RTNG |
| ARO / ARO-C1 | `aro` / `aro_cut1` | Q-ARO |
| TPR / PTP / APRO / APPO | `tpr` / `ptp` / `apro` / `appo` | Q-TPR / Q-PTP / Q-APRO / Q-APPO |
| DE (group stage; no scalar) | positional stage (scalar `direct_encounter` refused under fide-2024) | Q-DE |
| MPvGP / EMMSB / EMGSB / EGMSB / EGGSB / EDE(+chains) / SSSC / BC / TBR / BBE | team module (no ids minted) | T-* |
| buchholz_sum / arpo (non-FIDE / legacy) | frozen legacy ids | X-LEGACY |
