# FIDE sources consulted (this mission)

Retrieval: live web, 2026-10-02. Direct Handbook chapter fetch timed out
(full article text NOT machine-retrieved — re-retrieve before Phase 2);
content below is graded accordingly. Third-party material is never
authoritative.

## PRIMARY — official FIDE

1. FIDE Handbook C.07 pre-2023 chapter (handbook.fide.com, excerpts):
   BH §4.1, Median §4.2, Median-2 §4.3, Cut-1 §4.4, Cut-2 §4.5, DE §5.1
   ("If all the tied players have met each other, the sum of points from
   these encounters is used"), SB-RR §9.1, Sum of Buchholz §14.2.5.
2. FIDE Council PDF 2024_FC2_18 (doc.fide.com, "Play-Off and Tie-Break
   Regulations", approved 29/07/2024): SB §9.1 formula verbatim
   ("multiplying the final score of the opponents by the points scored
   against them"), BH final-round note, Art.16 pointer, Koya RR scope.
3. FIDE TEC Tie-Break Exercises V01-1 (tec.fide.com, 2024-04-16):
   worked BH(#2)=1.0+1.5+3.5+3.5+3.5=13.0 and
   BH-C1(#4)=3.5+3.5+3.0+1.5=11.5 on fully-played events; foreword
   confirms Aug-2023 regs abolished the virtual opponent and reworked
   unplayed-game management.
4. FIDE Handbook C.07 Aug-2024→Feb-2026 and Mar-2026→ chapters (index +
   excerpts): system table (§§6–10, BH-C1/ARO-C1/SB-C1/PS-C1 modifiers,
   VUR rule §16.5), Art.16 five-category taxonomy, approval 02/02/2026.

## SECONDARY — consistent, non-authoritative

5. @echecs/sonneborn-berger + @echecs/buchholz + @echecs/koya (MIT,
   zero-dep TS): section-scoped APIs, SB cut-variant semantics, VUR
   cut-exception pointer (§16.5.2). Candidates for MIT-compatible vector
   cross-checks, not definitions.
6. chesspairings.org tie-break guide (worked BH/BH-C1/BH-C2/Median/M2
   arithmetic examples; 28-system claim). Used to confirm trim
   direction; not a source for rules.
7. Lichess forum analysis of World Blitz 2024 tie-breaks (VUR §16.1.2 /
   §16.5.1 reapplication debate) — context on real-world ambiguity only.

## NOT retrieved (blockers for Phase 2)

- Full Article 16 text (16.3 adjusted scores, 16.4 draws-forth, 16.5 cut
  exception mechanics) beyond excerpts.
- Full §6 DE reapplication procedure, §10 rating-family conversion
  tables, §14 modifier mechanics.
