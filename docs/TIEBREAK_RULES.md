# Tie-break rules reference (informational — v0.1.0 does NOT reimplement FIDE)

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
Roadmap (new rules versions, never silent changes): Art.16, SB-C1/PS-C1/
ARO-C1, Median-2, AOB, ForeBH, TPR/PTP/APPO/RTNG, full DE league.
