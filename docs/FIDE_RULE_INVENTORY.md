# FIDE rule inventory (normative, atomic)

Every normative rule discovered this mission. `Affects` uses criterion
ids from `FIDE_CRITERIA_CATALOG.md`. `Status` is per §15 of the mission
(see `IMPLEMENTATION_ROADMAP.md` for the matrix)

| ID | Source / article | Rule | Affects | Rulesets | Status |
|---|---|---|---|---|---|
| R-ART2 | C.07 §2.1 | Silent regulations → rank via 2.2.2 + 4.1.1 | ranking sequence | 2024, 2026 | CONSUMER_OWNED (caller builds the list) |
| R-ART4.1 | C.07 §4.1–4.1.1 | Ordered list from Art 5 (organiser; arbiter completes + publishes pre-tournament) | ranking sequence | all | CONSUMER_OWNED |
| R-ART4.2 | C.07 §4.2 | Advance per still-tied subgroup (2026 wording); exhausted list → lots unless unbroken ties allowed | ranking engine | 2024, 2026 | IMPLEMENTED (successive-criteria ordering) |
| R-TYPES | C.07 §4.3 | Types A (multi-listable) / B / C / D-combos | sequencing | all | IMPLEMENTED (DE positional; docs) |
| R-MULTI | C.07 §4.4 | Repeated meetings count separately (except DE 6.1.2) | sums/avgs | all | IMPLEMENTED |
| R-DE-BASE | C.07 §6.1 | Mutual-encounter mini-standings | DE stage | all | IMPLEMENTED (fide-2024) |
| R-DE-FORFEIT | C.07 §6.1.1 | Forfeits excluded unless regulations opt in (Swiss scope) | DE stage | all | IMPLEMENTED |
| R-DE-AVG | C.07 §6.1.2 | Repeated meetings averaged (overrides 4.4) | DE stage | 2023→ | IMPLEMENTED (exact arithmetic) |
| R-DE-REAPPLY | C.07 §6.2 | Full meeting → standings decide; subsets reapply to stability | DE stage | 2023→ | IMPLEMENTED |
| R-DE-CERTAINTY | C.07 §6.3 | Swiss partial meeting → alone-at-top certainty, iteratively | DE stage | 2023→ | IMPLEMENTED |
| R-WIN | C.07 §7.1 | Win-point rounds, played or not | wins | all | IMPLEMENTED |
| R-WON | C.07 §7.2 | OTB wins only | won | 2024, 2026 | IMPLEMENTED (fide-2024) |
| R-BPG | C.07 §7.3 | OTB games with Black | games_black | 2024, 2026 | IMPLEMENTED (fide-2024) |
| R-BWG | C.07 §7.4 | OTB wins with Black | wins_black | 2024, 2026 | IMPLEMENTED (fide-2024) |
| R-PS | C.07 §7.5 | Σ cumulative scores (gap-filled) | progressive | all | IMPLEMENTED |
| R-REP | C.07 §7.6 | Rounds − HPB/ZPB/forfeit losses | rounds_elected | 2024, 2026 | IMPLEMENTED (fide-2024) |
| R-STD | C.07 §7.7 (2026) | Outscore/equal scheduled opponent (+draw-value unplayed) | std | 2026 | SPECIFIED (needs opp round scores) |
| R-TPN | C.07 §7.8 (2026) | Final pairing-number order (asc, or desc if regulated) | tpn | 2026 | SPECIFIED (needs pairing nos) |
| R-BH | C.07 §8.1 | Σ opponent final adjusted scores + §16.4 dummies | buchholz | all | IMPLEMENTED |
| R-RRBAN | C.07 Art 8 note (2026) | BH-family must not be used in round-robins | bh/aob/fb | 2026 | SPECIFIED (document; warn, don't hard-enforce) |
| R-AOB | C.07 §8.2 | Mean of OTB opponents' BH (2026: or FB) | aob | 2024, 2026 | IMPLEMENTED (BH-based) |
| R-FB | C.07 §8.3 | Final-round-as-draws BH + Art 16; dummy on FB points | fore_buchholz | 2024, 2026 | IMPLEMENTED |
| R-SB | C.07 §9.1 | Σ opp adjusted score × score vs them + §16.4 | sonneborn_berger | all | IMPLEMENTED |
| R-KOYA | C.07 §9.2 | Points vs ≥50%-of-maximum opponents (RR scope; limit §14.5) | koya | all | IMPLEMENTED (scope gating caller-side) |
| R-UNRATED | C.07 §10 preamble | Drop ratings TBs with unrateds unless pre-published handling | aro/tpr/ptp/apro/appo | 2024, 2026 | CONSUMER_OWNED (list selection) + documented |
| R-FIRSTRATING | C.07 §10 note (2026) | Multi-rating events use the FIRST rating | all §10 | 2026 | IMPLEMENTED-by-construction (single snapshot; contract) |
| R-ARO | C.07 §10.1 | Mean OTB opp rating, half-up int | aro/aro_cut1 | all | IMPLEMENTED |
| R-TPR | C.07 §10.2 + RR §8.1a | Rounded ARO + table RD of OTB fraction | tpr | 2024, 2026 | IMPLEMENTED |
| R-PTP | C.07 §10.3 + RR §8.1b | Lowest rating with ΣPD ≥ OTB score; 0 → −800; full scale | ptp | 2024, 2026 | IMPLEMENTED |
| R-APRO | C.07 §10.4 | Mean opp TPR, half-up int | apro | 2024, 2026 | IMPLEMENTED |
| R-APPO | C.07 §10.5 | Mean opp PTP, half-up int | appo | 2024, 2026 | IMPLEMENTED |
| R-RTNG | C.07 §10.6 (2026) | Rating order (desc, or asc if regulated) | rtng | 2026 | SPECIFIED (terminal; consumer key) |
| R-TEAM-* | C.07 §§11–13 | MP/GP, BC/TBR/BBE, MPvGP, ESB×4, EDE+chains, SSSC | team_* | all | OUT_OF_SCOPE (needs TeamMatch domain) |
| R-CUT1 | C.07 §14.1.1 | BH-C1/ARO-C1/PS-C1/SB-C1 value cuts (+team §14.1.2) | *_cut1 | 2024, 2026 | IMPLEMENTED (individual) |
| R-CUT2 | C.07 §14.2 | Two least-significant cuts (BH-C2 named) | buchholz_cut2 | all | IMPLEMENTED |
| R-MED1/2 | C.07 §§14.3–14.4 | Least(+most) cuts in order | median_* | all | IMPLEMENTED |
| R-LIMIT | C.07 §14.5 | Koya limit ±½ steps | koya variants | all | DEFERRED (generic limit machinery) |
| R-RR-FORFEIT | C.07 §15.2 (2024) | Pre-determined: forfeits = regular games | RR mode | 2024 | DEFERRED (no RR mode) |
| R-RR-FORFEIT26 | C.07 §15.2 (2026) | …except forfeits in §10, forfeit losses in Type B | RR mode | 2026 | SPECIFIED (RR mode rule) |
| R-VUR | C.07 §16.1.2 | VUR = requested bye or forfeit loss | all cuts | 2023→ | IMPLEMENTED |
| R-CAT | C.07 §16.2.1–16.2.5 | Five unplayed categories (positional early/late split) | art16 | 2023→ | IMPLEMENTED |
| R-ADJ | C.07 §16.3 | Opponent-side: .1–.4 face value, .5 as draws | bh/sb/ko | 2023→ | IMPLEMENTED |
| R-DUMMY24 | C.07 §16.4 (2024) | Dummy finishes on own score, uncapped | bh/sb | 2024 | IMPLEMENTED |
| R-DUMMY26 | C.07 §16.4.1–16.4.2 (2026) | Dummy ≤ scheduled-opp adjusted (forfeits) / ≤ draw×rounds (rest) | bh/sb | 2026 | SPECIFIED (fide-2026 core) |
| R-VURCUT | C.07 §16.5.1–16.5.2 | Cut lowest VUR contribution (SB: higher-of), reapplied | cuts | 2023→ | IMPLEMENTED |
| R-OPT OUT | C.07 §16.6 | Pre-announced alternatives to 16.3–16.5 | art16 | all | DEFERRED (no competition-reg input contract) |
| R-PAIR-BH/SB | C.04 Basic Rules §§1.7–1.8 | Pairing-time BH/SB on CURRENT scores + self-game + accel exclusion; bracket order BH→SB→TPN | pairing | 2026 | CONSUMER_OWNED (pairing-core, not this lib) |
| R-NORM-TPR | B.01 §§1.4.6–1.4.9 | Norm Rp: floors, imputed 1400, 35% min — NOT tiebreak TPR | — | all | OUT_OF_SCOPE (documented warning) |

Rules with `UNVERIFIED` article blame: none — every row above was read
in a primary text this mission except the Apr-2024 clarifications
(which FIDE itself declares definition-neutral).
