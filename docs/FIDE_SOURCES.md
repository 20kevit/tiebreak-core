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

## NOT retrieved (remaining blockers)

- FIDE Handbook C.07 March-2026 edition full text (only index +
  excerpts). Consequence: the implemented engine is ruleset `fide-2024`
  (fully sourced above); `fide-2026` stays reserved until the 2026
  full-text diff is retrieved and reviewed.
- FIDE Rating Regulations conversion tables (needed for TPR/PTP and
  hence APRO/APPO) — those systems stay unimplemented.
