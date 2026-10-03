# Software comparison (secondary sources; behavior is never normative)

Conventions: **[FIDE RULE]** = in C.07 text; **[SOFT CONV]** =
software's own choice; **[WORKAROUND]** = non-FIDE/transitional.
All below is SECONDARY (vendor docs, READMEs, changelogs, KB articles).

## Result matrix

| System | Tech | Tie-break? | C.07 edition | Unplayed model | DE | Ratings | Precision | Versions |
|---|---|---|---|---|---|---|---|---|
| `@echecs/*` (echecsjs) | TS, MIT, zero-dep, ESM | yes (section-scoped pkgs + `tiebreak` alias) | Mar-2026 (SPEC.md quotes) | `Game.kind` 6-value + Art 15/16 incl. VUR/16.5 | base + `/forfeits` opt-in (§6.1.1) | ARO/TPR/PTP/APRO/APPO; 15.2 forfeit-exclusion (4.1.0) | float sums; half-up at averages | per-pkg semver, no multi-edition switch |
| Gacrux / TieBreakServer (→FIDE, MIT, Python ≥3.11) | reference checker | yes, full + team | 2026 (`MTB26` codes) | full Art 16 (`-p`/`-s` modes) | full incl. EDE/ESB | full + team variants | per-spec | single live reference; RTG seeds |
| Vega | native, proprietary/free-Linux | yes (Gacrux engine since 12.0.0) | Baku-2023 default + 2026 via Gacrux | Art 16 + national toggles (`H_PAB`) **[WORKAROUND]** | yes | ARO/TPR family | closed | endorsement pinned per version |
| Swiss-Manager / chess-results.com | Delphi/Win, proprietary | yes (ordered list UI, parametrised BH) | Baku-2023 toggle (14.0.0.70); Gacrux activated 04-2026 | closed | yes | SB/WIN + ratings | closed | version-pinned endorsement |
| SwissSys | Win shareware, proprietary | yes (standard list) | Minsk-2018 endorsement; no public 2026 delta | closed | closed | closed | closed | version-pinned |
| Tornelo | SaaS, proprietary | yes (param UI) | "100% accurate", edition unstated | virtual-opponent toggle **[WORKAROUND]** (abolished 2023 **[FIDE RULE]**) | forfeit/colour switches **[SOFT CONV]** | ARO family | closed | cloud, no pin |
| WinTD | proprietary (Estima) | yes (large FIDE+USCF matrix; best naming cross-check: Solkoff=BH, Cumulative=PS) | current | closed | yes | yes | closed | versioned |
| JaVaFo | Java, closed freeware | **no** — Dutch pairing (C.04) reference | — | TRF bye/result codes (consumed by others) | — | — | — | pinned jar |
| bbpPairings | C++, Apache-2.0 | **no** — Dutch/Burstein pairing engine | — | — | — | — | — | release tags |
| python-chess | Python, GPL-3.0 | **no** (verified: board/PGN/UCI only) | — | — | — | — | — | — |
| ChessPairings.org | free, **not FIDE-endorsed** | 28 systems (bbpPairings-v6 + Gacrux) | Mar-2026 guide | VUR prose + Virtual-Opponent note | yes | yes | docs | live |
| py4swiss (MIT) | pairing only | no | — | — | — | — | — | — |

Key lessons for tiebreak-core: pairing endorsement ≠ tie-break
certification (FIDE endorses pairing-engine versions; tie-break lists
are vendor-maintained); never copy virtual-opponent or forfeit toggles
into `fide-2024`; section-scoped signatures
`(player,games)` vs `(player,games,players)` + co-located SPEC quotes
+ per-criterion CHANGELOGs are worth borrowing (echecsjs); Gacrux
RTG-seeded TRF corpora are the best differential source; the highest
bug-density area everywhere is VUR/cut-exception handling.

Useful vectors: TEC worked BH 13.0 / BH-C1 11.5 (PRIMARY, in-corpus);
echecsjs vitest suites (MIT oracle); ChessPairings.org smoke numbers
(BH 26 vs 23.5, BH-C1 22, SB 10 = 4+3+1.75+1.25 — SECONDARY).
