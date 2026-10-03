# TRF26 interoperability ( लड़ाई boundary)

Primary source: TRF26 Format v2026 (C.02 Annexure A; approved
12/05/2025, applied 01/09/2025; 638-line extraction, hash in
registry) + TournamentTypeCodeTable(192) + MTB26. TRF26 is the agreed
format for rating submission, pairing/tie-break testing, and
**in-tournament data exchange (ITDX)** between THPs and engines.

## Fields affecting tie-break calculation

- **202 / 212**: ordered MTB26 descriptors (212 adds `PTS` = points /
  primary points; "212 PTS," ≡ "202"). THE criterion sequence —
  consumer-owned, core-consumable as `criteria` order.
- **192**: tournament-type code (Swiss/RR/team/knockout…): selects the
  format-variant regime (Art 15 vs 16, BH-ban, team codes).
- **001 player records + per-round fields**: opponent TPN, colour
  w/b, game points, forfeit flag `f`; bye acronyms FPB/HPB/ZPB/PAB
  (case-insensitive).
- **013 scoring system**: W/D/L/A/P/X point values (default
  1/½/0/0/PAB-as-W/X-as-D; configurable) — the event table STD
  (§7.7) comparisons need; mandatory when deviating from defaults.
- **240/320 bye records**: FPB/HPB/ZPB recipients per round; team PAB
  MP/GP values per round.
- **250/260 acceleration records**: fictitious points (pairing-only;
  excluded from tie-breaks per C.04 — must not leak into core inputs).
- **310/801/802 team records**: MP/GP, board-by-board results,
  forfeit indicators — future team-module inputs.
- **Rating-source codes** (FIDON/NIDOF/HBFN/LBFN/OTHER + starting-rank
  method): select the FIRST-rating snapshot feeding §10 (D9).

## Responsibility split (normative for adapters)

```text
TRF parser (consumer/THP side)            vs   tiebreak-core domain inputs
- parse 001/240/320/801/802/013/192            - PlayerTiebreakData (id, FIRST rating, final points, games)
- map W/D/L/A/P/X + 013 table → 1/½/0          - GameRecord (opp id [-1 virtual], score, color, round, kind)
- map FPB/HPB/ZPB/PAB/f → GAME_KINDS           - criteria order ← 202/212 descriptor list (MTB26 ids)
  (+ positional 16.2.3/16.2.5 split)           - total_rounds, Swiss/RR mode flag (fide-2026), pairing nos (TPN)
- resolve scheduled opponents (16.4.1)         - NEVER sums points, NEVER pairs, NEVER reads TRF
- select FIRST rating snapshot                 - raises typed errors on uncategorized -1 / incoherence
```

The core must accept MTB26 descriptor strings (incl. `OTHER_*`
pass-through at parse level) and MUST NOT implement TRF parsing —
zero-dependency policy + boundary above. A TRF reader, when needed,
lives in chess-manager/THP land and is tested against the 801/802
fixtures quoted in the TRF26 text.

## ETT26 — field 192 classification (C.02.03 Annex C)

TRF26 field 192 carries an ETT26 tournament-type code
(`FIDE_DUTCH_*`, `BERGER_ROUNDROBIN_Gn`, `FIDE_TEAM_*`,
`CUSTOM_*`, … — full table: `FIDE_TEC_IMPLEMENTATION_REQUIREMENTS.md`
§ETT26; registry SRC-ETT26). Architectural chain (consumer-owned
until the last step):

```text
TRF26 field 192
        ↓  (consumer/THP: TRF parsing + ETT26 lookup)
tournament/format classification
        ↓  (consumer: explicit regime mapping — Swiss / predetermined /
            team-Swiss / team-RR / knockout / custom; CUSTOM_* never inferred)
C.07 format regime (§15.2 vs §16; BH-ban; team codes)
        ↓
tie-break semantics + descriptor list (202/212)
        ↓  (normalized request: players, games+kinds, criteria, total_rounds, mode)
tiebreak-core calculation
```

`tiebreak-core` must NOT become a TRF parser merely because ETT26
exists, and must NOT embed the ETT26 table: the adapter owns parsing,
lookup, and conversion into normalized domain semantics (including
the future Swiss/RR mode flag). ETT26 version drift (e.g. the
DUTCH_2025→2026 cutover change) is therefore a consumer data-update,
never a core behavior change.
