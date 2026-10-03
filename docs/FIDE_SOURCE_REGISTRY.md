# FIDE source registry

Primary = official FIDE origin. Hashes are of the local extractions
(byte-identical source PDFs noted); PDFs themselves are NOT committed
(licensing caution per §26) — URLs + hashes reproduce retrieval.
`repository file` = extraction location at mission time (`/tmp` files
are session-local; hashes let any engineer re-verify).

| source_id | official_title | publisher | publication | effective | URL / doc id | retrieval | SHA256 (extraction) | scope | authority | supersedes → superseded_by | repo file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SRC-C07-2022 | Tie-Break Regulations (2022 text) | FIDE (SPP) | 2022-06-29 (draft header) | 2023-07-01 | spp.fide.com/.../20220629-Tie-Breaks-2.pdf | 2026-10-03 | pdf `10549bac…` | pre-2023 regime | PRIMARY | — → SRC-C07-2023 | /tmp/opencode/20220629-Tie-Breaks-2.pdf |
| SRC-TOC-2023 | C.07 Table of Changes (Sep-2023 rewrite) | FIDE Council 2FC2023 | 2023 | 2023-09-01 | doc.fide.com/.../PO_and_TB_Regulations_Table_of_Changes.pdf | 2026-10-03 | — (203-line extraction) | rewrite diff | PRIMARY | SRC-C07-2022 → SRC-C07-2024A | /tmp/opencode (session) |
| SRC-C07-2024A | C.07 decision (Apr-2024) | FIDE Council 3FC2023/43 | 2023-12-14 | 2024-04-01 | doc.fide.com/.../FC3_2023_43.pdf | 2026-10-03 | 396-line extraction | clarifications | PRIMARY | SRC-C07-2023 → SRC-C07-2024B | session |
| SRC-C07-2024B | Play-Off and Tie-Break Regulations | FIDE Council 2024_FC2_18 | 2024-07-29 | 2024-08-01 | doc.fide.com/.../2024_FC2_18.pdf | 2026-10-02 | pdf `fc7fed37…`; txt `ff475da4…` | `fide-2024` basis | PRIMARY | SRC-C07-2024A → SRC-C07-2026 | /tmp/fide2024.txt |
| SRC-TOC-2024 | C.07 Table of Changes (Annex 5.5.2b) | FIDE Council 2FC2024 | 2024 | 2024-08-01 | doc.fide.com/.../2024_FC2_18_TOC.pdf | 2026-10-03 | pdf `3364d0f5…`; txt `e5b2ca5d…` | editorial proof | PRIMARY | — | /tmp/opencode/TOC2024.txt |
| SRC-C07-2026 | Play-Off and Tie-Break Regulations | FIDE Council (02/02/2026; instrument no. UNVERIFIED) | 2026-02-02 | 2026-03-01 | handbook.fide.com/chapter/TieBreakRegulations032026 (via Arbiter Manual 2026 pp.248–261) | 2026-10-03 | manual pdf `c72990f2…`; extraction `6ec614b4…` | current rules | PRIMARY | SRC-C07-2024B → current | /tmp/opencode/c07-2026.txt |
| SRC-TEC-EX | Tie-Break Exercises V01-1 (Held) | FIDE TEC | 2024-04-16 | — (C.07-2023 basis) | tec.fide.com/.../C.07-2023-Tiebreak-exercises-V01-1.pdf | 2026-10-03 | pdf `42255c32…`; txt `66906e9e…` | worked examples | PRIMARY | — | /tmp/opencode/tec-exercises.txt |
| SRC-MTB26 | Mandatory Tie-Breaks (MTB26) | FIDE (Handbook attach.) | 2025–2026 | 2026-03-01 (codes) | handbook.fide.com/files/handbook/MTB26.pdf | 2026-10-03 | draft pdf `5c3b7548…`; extraction `622330bd…` | approval code set | PRIMARY | TRF25-draft → MTB26 | /tmp/opencode/MTB26.txt |
| SRC-TRF26 | TRF Format v2026 (Annexure A) | FIDE Council (Ricca) | 2025-05-12 | 2025-09-01 | handbook.fide.com/files/handbook/TRF26.pdf | 2026-10-03 | pdf `0fa6bf9f…`; txt `56e205d9c…` | interchange | PRIMARY | TRF16 → current | /tmp/opencode/TRF-2026.txt |
| SRC-TTCT192 | TournamentTypeCodeTable(192)-TRF26 | FIDE TEC | 2025-04 | 2025-09-01 | tec.fide.com/.../TournamentTypeCodeTable192-TRF26.pdf | 2026-10-03 | pdf `5513ac8d…` | 192 codes | PRIMARY | — | /tmp/opencode/TTCT192.pdf |
| SRC-TECMAN | TEC Policies & Procedures Manual v1.24 | FIDE TEC | 2026-03-07 | — (process) | tec.fide.com/.../FIDE-TEC-Manual-01.24.pdf | 2026-10-03 | pdf `70638fe2…`; txt `fa0d737d…` | approval/testing | PRIMARY (Handbook prevails) | v1.23 → v1.24 | /tmp/opencode/TEC-Manual-01.24.txt |
| SRC-CONG26 | TEC Congress paper (Samarkand 2026) | FIDE TEC | 2026-09 | — | tec.fide.com/.../TEC-2026-Congress-Meeting.pdf | 2026-10-03 | snippets | C.02/C.04 restructure, Gacrux status | PRIMARY | — | indexed text |
| SRC-C04-2026 | Basic Rules for Swiss Systems | FIDE Council CM3-202517 | 2025-10-28 | 2026-02-01 | doc.fide.com/.../CM3-202517.pdf | 2026-10-03 | §§1.6–1.8 extraction | pairing boundary | PRIMARY | — | session |
| SRC-RR-2024 | Rating Regulations (eff. 1 Mar 2024) | FIDE Council FC3_2023_25 | 2023-12 | 2024-03-01 | doc.fide.com/.../FC3_2023_25.pdf | 2026-10-03 | §§8.1.1/8.1.2 verbatim | tables 8.1a/b | PRIMARY | 2022 → current | session |
| SRC-B01-2024 | Title Regulations (eff. 1 Jan 2024) | FIDE Council FC3_2023_26 | 2023-12 | 2024-01-01 | doc.fide.com/.../FC3_2023_26.pdf | 2026-10-03 | §§1.4.6–1.4.9 verbatim | norm-TPR warning | PRIMARY | — | session |
| SRC-RATING22 | Rating Regulations (eff. 1 Jan 2022) | FIDE | 2022 | 2022-01-01 | fide.com/.../FIDE Rating Regulations 2022.pdf | 2026-10-02 | pdf `41fbd8d0…` | table source | PRIMARY | — → SRC-RR-2024 | /tmp/fide_rating2022.pdf |
| SRC-NEWS26-C07 | C.07 reminder 25 Mar 2026 | FIDE | 2026-03-25 | 2026-03-01 | fide.com/...effective-march-1-2026 | 2026-10-03 | page text | rationale | PRIMARY | — | indexed text |
| SRC-NEWS26-C02 | C.02 reminder 1/26 Mar 2026 | FIDE | 2026-03 | 2026-03-01 | fide.com/...chess-equipment-regulations... | 2026-10-03 | page text | C.02 in force | PRIMARY | — | indexed text |

Secondary (discovery only, never normative): echecsjs SPEC/README set
(MIT), ChessPairings.org guide, WinTD matrix, vendor changelogs
(Vega/Swiss-Manager/Tornelo/SwissSys), Lichess forum analysis,
checkmat.net/vibechess walk-throughs, chess-results annotations,
democraticchess online-tournament notes. Full prose in
`SOFTWARE_COMPARISON.md`; each claim tagged there.
| SRC-OLY26 | Olympiad 2026 Main Competition Regulations (App. 2.I–2.IV) | FIDE | 2026 | 2026 | handbook.fide.com/files/handbook/Olympiad2026MainCompetition.pdf | 2026-10-03 | indexed text | TB1=ΣIS(10)/TB2=GP/TB3=ΣMP(10); combined TB1–TB4; board TPR; unplayed-match formulas | PRIMARY (event regs) | — | indexed text |
| SRC-FTM | FIDE Technical Manual (FTM) page | FIDE TEC | — (stub 2026-03-24, no content) | — | tec.fide.com/fide-technical-manual | 2026-10-03 | stub (negative result) | none yet; substantive manual = SRC-TECMAN | n/a | — | stub |
| SRC-CONG26 | TEC Congress paper Samarkand 2026 | FIDE TEC | 2026-09 | — | tec.fide.com/.../TEC-2026-Congress-Meeting.pdf | 2026-10-03 | indexed text | C.02/C.04 restructure; Gacrux; VCL pending; tie-break testing future | PRIMARY | — | indexed text |
