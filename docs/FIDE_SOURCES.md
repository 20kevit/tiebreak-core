# FIDE sources consulted (this mission)

Retrieval: live web, 2026-10-02/03. Direct Handbook chapter fetch timed
out repeatedly; the complete official text below was retrieved IN FULL
via alternate official path (doc.fide.com PDF + local text extraction).

## PRIMARY — official FIDE (full text retrieved)

0. FIDE Council document 2024_FC2_18
   (`https://doc.fide.com/docs/DOC/2FC2024/2024_FC2_18.pdf`,
   "PLAY-OFF AND TIE-BREAK REGULATIONS", approved by FIDE Council on
   29/07/2024, applied 1 Aug 2024 for all FIDE competitions):
   RETRIEVED IN FULL (653-line text extraction). Basis for ruleset
   `fide-2024`. Covers: system table + Cut-1 flags (Art.5), DE §6
   (6.1/6.1.1/6.1.2/6.2/6.3 incl. Swiss conditional ranking),
   Type-B §§7.1–7.6 (WIN/WON/BPG/BWG/PS/REP), BH family §§8.1–8.3
   (BH/AOB/FB), SB §9.1 + Koya §9.2 (RR-only, 50% of maximum possible),
   rating family §§10.1–10.5, team systems §§11–13, modifiers §§14.1–14.6
   (incl. SB-C1 14.1.1.d, Median order 14.3/14.4, Koya limit 14.5),
   unplayed rounds §§15.1–15.3, full Article 16
   (16.1 VUR/requested-bye, 16.2 five categories, 16.3 adjusted scores,
   16.4 dummy rule, 16.5/16.5.2 cut exception, 16.6 local override).

1. FIDE Rating Regulations §8.1a (p→dp, 101 entries) and §8.1b
   (D→PD, 51 bands), extracted in full from the official PDF "FIDE
   Rating Regulations effective from 1 January 2022"
   (fide.com/docs/regulations/FIDE Rating Regulations 2022.pdf) via
   layout-preserving text extraction; completeness (101/101 values,
   0–735 gapless coverage) and dp symmetry verified programmatically.
   Basis for `tpr`/`ptp`/`apro`/`appo` under fide-2024.

## PRIMARY — official FIDE (excerpts)


2. FIDE Handbook C.07 pre-2023 chapter (handbook.fide.com, excerpts):
   BH §4.1, Median §4.2, Median-2 §4.3, Cut-1 §4.4, Cut-2 §4.5, DE §5.1
   ("If all the tied players have met each other, the sum of points from
   these encounters is used"), SB-RR §9.1, Sum of Buchholz §14.2.5.
3. FIDE Council PDF 2024_FC2_18 (doc.fide.com, "Play-Off and Tie-Break
   Regulations", approved 29/07/2024): SB §9.1 formula verbatim
   ("multiplying the final score of the opponents by the points scored
   against them"), BH final-round note, Art.16 pointer, Koya RR scope.
4. FIDE TEC Tie-Break Exercises V01-1 (tec.fide.com, 2024-04-16):
   worked BH(#2)=1.0+1.5+3.5+3.5+3.5=13.0 and
   BH-C1(#4)=3.5+3.5+3.0+1.5=11.5 on fully-played events; foreword
   confirms Aug-2023 regs abolished the virtual opponent and reworked
   unplayed-game management.
5. FIDE Handbook C.07 Aug-2024→Feb-2026 and Mar-2026→ chapters (index +
   excerpts): system table (§§6–10, BH-C1/ARO-C1/SB-C1/PS-C1 modifiers,
   VUR rule §16.5), Art.16 five-category taxonomy, approval 02/02/2026.

## SECONDARY — consistent, non-authoritative

6. @echecs/sonneborn-berger + @echecs/buchholz + @echecs/koya (MIT,
   zero-dep TS): section-scoped APIs, SB cut-variant semantics, VUR
   cut-exception pointer (§16.5.2). Candidates for MIT-compatible vector
   cross-checks, not definitions.
7. chesspairings.org tie-break guide (worked BH/BH-C1/BH-C2/Median/M2
   arithmetic examples; 28-system claim). Used to confirm trim
   direction; not a source for rules.
8. Lichess forum analysis of World Blitz 2024 tie-breaks (VUR §16.1.2 /
   §16.5.1 reapplication debate) — context on real-world ambiguity only.

## PRIMARY — official FIDE (retrieved 2026-10-03, research mission)

8. Play-Off and Tie-Break Regulations effective 1 Mar 2026
   (approved by FIDE Council 02/02/2026), full text extracted from
   pp.248–261 of the official FIDE Arbiters' Manual 2026
   (`https://arbiters.fide.com/wp-content/uploads/Publications/Manual/Arbiter-Manual-2026.pdf`):
   RETRIEVED IN FULL (630-line extraction). Includes the six-example
   unplayed-games annex (Laxman + Examples 01–06, OLD/NEW columns).
   Word-level diff vs item 0 produced `docs/FIDE_2026_DIFF.md`
   (15 semantic deltas D1–D15); corpus `tests/corpus/fide2026_unplayed.json`.
9. FIDE TEC Tie-Break Exercises V01-1 (Rev.2403220900 / C.07-2023,
   IA Mario Held, 2024-04-16,
   `https://tec.fide.com/wp-content/uploads/2024/04/C.07-2023-Tiebreak-exercises-V01-1.pdf`):
   RETRIEVED IN FULL (3644-line extraction). Worked BH/BH-C1/AOB/FB/SB/Koya/TPR/APRO/PTP/DE
   chapters; Example 06 (BH-C1 11.5) encoded as corpus `TEC-EX06-2024-BHC1` (VERIFIED).
10. C.07 Table of Changes Aug-2024 (`https://doc.fide.com/docs/DOC/2FC2024/2024_FC2_18_TOC.pdf`,
    Annex 5.5.2b): RETRIEVED — proves the 2024 changes editorial-only.
11. C.07 Table of Changes Sep-2023 (`https://doc.fide.com/docs/DOC/2FC2023/PO_and_TB_Regulations_Table_of_Changes.pdf`)
    + 2022 text (`https://spp.fide.com/wp-content/uploads/20220629-Tie-Breaks-2.pdf`)
    + Apr-2024 decision (`https://doc.fide.com/docs/DOC/3FC2023/FC3_2023_43.pdf`):
    RETRIEVED — basis of `docs/FIDE_RULESET_HISTORY.md`.
12. FIDE announcement `fide.com/…updated-play-off-and-tie-break-regulations-effective-march-1-2026`
    (25 Mar 2026): RETRIEVED — confirms STD/TPN/RTNG rationale, BH/SB unplayed revision,
    team-KO provisions, rating/Type-B unplayed handling.
13. C.04 Basic Rules for Swiss Systems (Council 28/10/2025, applied 1 Feb 2026,
    `https://doc.fide.com/docs/DOC/2025_3FC/CM3-202517.pdf`): RETRIEVED (§§1.6–1.8) —
    pairing-time opposition evaluation belongs to pairing-core (see gap analysis).
14. Rating Regulations 1 Mar 2024 (`https://doc.fide.com/docs/DOC/3FC2023/FC3_2023_25.pdf`)
    + Title Regulations (`.../FC3_2023_26.pdf`): RETRIEVED — tables 8.1a/8.1b unchanged
    (still current; Oct-2025 400/2650 amendment touches rating calc only, and C.07 §10.3
    uses the full scale regardless); B.01 norm-TPR ≠ C.07 TPR (floors/imputed 1400/35%).

## NOT retrieved (residual)

- Live Handbook chapter HTML (handbook.fide.com times out from here; mirror
  handbook1090 likewise). Covered via items 8–11 (official PDFs/manual).
- 02/02/2026 approving instrument number/URL (UNVERIFIED; dates RETRIEVED).
- WRBC 2025 regulation PDF fine print (MEDIUM confidence via snippets; no core impact).
