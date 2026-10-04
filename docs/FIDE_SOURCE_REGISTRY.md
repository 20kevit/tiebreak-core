# FIDE source registry (auditable index)

Provenance detail lives in `FIDE_SOURCES.md` (retrieval narrative) and
`FIDE_2026_DIFF.md` (2024→2026 word diff). This file is the structured
index: one row per source with authority, coverage, and verification
status. Status vocabulary: VERIFIED (full text retrieved and checked),
CROSS-CHECKED (excerpt/index confirmed against a VERIFIED source),
UNVERIFIED (claimed but not confirmed), UNREACHABLE (endpoint failed;
content covered another way — never a downgrade of the source itself).

No official Handbook endpoint is invented below. Where the live
Handbook was unreachable, the covering official PDF/manual is named.

| ID | Title / edition | Approved | Effective | URL | Type / authority | Covers (core use) | Status |
|---|---|---|---|---|---|---|---|
| SRC-C07-2024 | FIDE Council 2024_FC2_18, Play-Off and Tie-Break Regulations | 29/07/2024 | 01/08/2024 | https://doc.fide.com/docs/DOC/2FC2024/2024_FC2_18.pdf | PRIMARY official PDF, full text (653-line extraction at retrieval) | Ruleset fide-2024: Arts.5–10, 14 (incl. SB-C1 14.1.1.d, Koya limit 14.5), 15, 16 | VERIFIED |
| SRC-C07-2026 | Play-Off and Tie-Break Regulations, FIDE Arbiters' Manual 2026 pp.248–261 | 02/02/2026 | 01/03/2026 | https://arbiters.fide.com/wp-content/uploads/Publications/Manual/Arbiter-Manual-2026.pdf | PRIMARY official manual, full text (630-line extraction) + six-example annex | Ruleset fide-2026: D1–D15, §16.4 caps, new §§7.7/7.8/10.6, §15.2 carve-out | VERIFIED (Council instrument number UNVERIFIED; dates VERIFIED) |
| SRC-RR-2022 | FIDE Rating Regulations effective 1 Jan 2022 | 2021 Council | 01/01/2022 | fide.com/docs/regulations/FIDE Rating Regulations 2022.pdf | PRIMARY official PDF, full §§8.1a (101 entries) + 8.1b (51 bands) extraction | Rating tables for tpr/ptp/apro/appo (embedded verbatim; programmatic completeness check) | VERIFIED |
| SRC-RR-2024 | Rating Regulations 1 Mar 2024 + Title Regulations | 2023 Council | 01/03/2024 | https://doc.fide.com/docs/DOC/3FC2023/FC3_2023_25.pdf (+26) | PRIMARY official PDF | Confirms 8.1a/8.1b unchanged; B.01 norm-TPR ≠ C.07 TPR | VERIFIED |
| SRC-TEC-EX | FIDE TEC Tie-Break Exercises V01-1 (Rev.2403220900, C.07-2023) | 16/04/2024 | — (training) | https://tec.fide.com/wp-content/uploads/2024/04/C.07-2023-Tiebreak-exercises-V01-1.pdf | Official TEC technical, full text (3644-line extraction) | Worked BH/BH-C1/AOB/FB/SB/SB-C1/Koya/TPR/APRO/PTP/DE; corpus TEC cases | VERIFIED |
| SRC-TOC-2024 | C.07 Table of Changes Aug-2024 (Annex 5.5.2b) | 2024 | 01/08/2024 | https://doc.fide.com/docs/DOC/2FC2024/2024_FC2_18_TOC.pdf | PRIMARY official annex | Proves 2024 changes editorial-only | VERIFIED |
| SRC-HIST | C.07 Table of Changes Sep-2023 + 2022 text + Apr-2024 decision FC3_2023_43 | 2022–2024 | various | doc.fide.com (2FC2023 PO_and_TB_Table_of_Changes; 3FC2023 FC3_2023_43) + spp.fide.com 20220629-Tie-Breaks-2.pdf | PRIMARY official PDFs | Ruleset history (`FIDE_RULESET_HISTORY.md`); legacy/Median-2 definitions | VERIFIED |
| SRC-STD-ANNOUNCE | FIDE announcement: updated play-off/tie-break regulations effective March 1 2026 | 25/03/2026 | 01/03/2026 | fide.com updated-play-off-and-tie-break-regulations-effective-march-1-2026 | Official announcement | STD/TPN/RTNG rationale, BH/SB revision | VERIFIED |
| SRC-C04-2026 | C.04 Basic Rules for Swiss Systems (applied 1 Feb 2026) | 28/10/2025 | 01/02/2026 | https://doc.fide.com/docs/DOC/2025_3FC/CM3-202517.pdf | PRIMARY official PDF (§§1.6–1.8) | Pairing-time evaluation → pairing-core (out of core scope) | VERIFIED |
| SRC-HB-PRE2023 | FIDE Handbook C.07 pre-2023 chapter excerpts | — | till 31/08/2023 | handbook.fide.com (excerpts) | Official handbook excerpts | BH §4.1, Median §§4.2–4.3, Cut §§4.4–4.5, DE §5.1, Sum-of-Buchholz | CROSS-CHECKED |
| SRC-HB-2026-IDX | FIDE Handbook C.07 Mar-2026 chapter index + excerpts | 02/02/2026 | 01/03/2026 | handbook.fide.com (index) | Official index | Cross-check of SRC-C07-2026 (system table, Art.16 taxonomy, approval date) | CROSS-CHECKED |
| SRC-C0203 | C.02.03 software/THP requirements + ETT26 Annex C | — | 2026 | C.02 framework (see `FIDE_TEC_IMPLEMENTATION_REQUIREMENTS.md`) | Official framework | THP/approval context; ETT26 field-192 regime mapping (consumer-side) | CROSS-CHECKED |
| SRC-TRF26 | TRF26 Format v2026 (C.02 Annexure A) | 12/05/2025 | 01/09/2025 | C.02 Annexure A (638-line extraction per repo docs) | PRIMARY official format | Fields 202/212 (MTB26 order), 192 (regime), 001/round fields, 013 (scoring table) — consumer-side parser | CROSS-CHECKED |
| SRC-MTB26 | MTB26 mandatory tie-break program table (Handbook version governs) | 2025 | 2026 | Handbook MTB26 chapter (141-line draft extraction cross-checked; STD 7.7 / TPN 7.8 / RTNG 10.6 rows verified present) | PRIMARY official table | Modifier/code inventory (`FIDE_MTB26_CATALOG.md`); `OTHER_*` rule | CROSS-CHECKED |
| SRC-SEC-IMPL | @echecs/* (MIT TS), chesspairings.org guide, Lichess WC Blitz analysis | — | — | public web | SECONDARY, non-authoritative | Trim direction, SB-cut pointers, ambiguity context only | UNVERIFIED (by design; never normative) |

## Live-endpoint limitations (recorded, not worked around by invention)

Note (2026-10-03 re-check): Handbook chapter/file hosts
(`handbook.fide.com`, `handbook1090.fide.com`) remain unreachable by direct
fetch (connection timeout, three attempts incl. static-file URLs); the C.07
2026 normative text therefore still rests on the Arbiter Manual 2026
extraction (SRC-C07-2026) cross-checked against Handbook indexed text.
Approval date 02/02/2026 = VERIFIED (manual header + Handbook index);
effective date 01/03/2026 = VERIFIED; Council instrument number =
UNVERIFIED (an unverified instrument number does not weaken the verified
dates — recorded separately by design).

## In-repo verification artifacts (evidence, not sources)

- Embedded rating tables (`fide2024.py` `_DP_BY_HUNDREDTH` 101 entries,
  `_PD_RANGES` 51 bands): values transcribed from SRC-RR-2022;
  programmatic spot-checks in `tests/test_ratings.py` + brute-force
  cross-verification noted there.
- Official corpus (`tests/corpus/*.json`): each VERIFIED case names its
  source row above; classification OFFICIAL_PRINTED_VALUE vs
  definition-derived is tracked per-case in `notes` (see report Stage 8).
