# FIDE MTB26 catalog (Mandatory Tie-Breaks, TRF26)

Primary sources (both retrieved 2026-10-03; extraction hashes in
`FIDE_SOURCE_REGISTRY.md`):

- `MTB26.pdf` — `https://handbook.fide.com/files/handbook/MTB26.pdf`
  (Handbook attachment, current; TRF26 labels). Content verified via
  search-index text (Handbook file host unreachable from here).
- `MandatoryTieBreaks-TRF26.pdf` — `http://tec.fide.com/wp-content/uploads/2025/04/MandatoryTieBreaks-TRF26.pdf`
  (TEC pre-release draft; labels records as TRF25 and notes
  *"The FIDE Handbook will be updated in 2025"*). Full 141-line
  extraction read. Rule content identical to the Handbook version
  except: the draft's per-section tables omit the STD/TPN/RTNG rows
  that the Handbook version carries (verified present in the Handbook
  text: `STD 7.7`, `TPN 7.8 ●`, `RTNG 10.6 ●`). Where they differ,
  the Handbook version governs.

Purpose (MTB26 §1): every tie-break a **FIDE-approved program must
implement**, each with a Rank Order Descriptor used in TRF26 records
202/212. Organiser self-defined criteria travel as `OTHER_<code>`
(C.07 §4.1).

## Descriptor grammar

```text
Name[:Teamscore][/Variant]...        (case-insensitive)
Name      = C.07 §5 acronym (BH, SB, DE, …; ESB sub-acronyms EMMSB/EMGSB/EGMSB/EGGSB; EDE chains)
:MP / :GP = team reference score (individual criteria reused for teams, C.07 §13 blanket rule)
Variant   = /Cn (Cut n: C1, C2, …) | /Mn (Median n: M1, M2, …) | /L±n (Koya limit shift in half-points)
          | /Kx (SSSC normaliser redefinition) | /P (forfeits-as-played) | /F (Fore-BH instead of BH)
          | /R (reverse order: TPN/R, RTNG/R)
```

`/P` text cites "Article C.07.16.5" — a document typo (16.5 is the
cut exception); the behavior is the §6.1.1 forfeit-inclusion opt-in
(recorded as an official-text slip, behavior unambiguous from C.07).
`x` in the code table = "any reasonable value must be implemented"
(generic-Cn/Mn/Lx/Kx machine).

## Table 1 — individuals only

| identifier | official_name | § | allowed modifiers/options | ruleset | implementation_status |
|---|---|---|---|---|---|
| DE, DE/P | Direct Encounter | 6 | /P | fide-2024 + fide-2026 | IMPLEMENTED (group stage; /P flag under fide-2026) |
| BPG | Games Played w/ Black | 7.3 | — | fide-2024 | IMPLEMENTED |
| BWG | Games Won w/ Black | 7.4 | — | fide-2024 | IMPLEMENTED |
| REP | Rounds Elected to Play | 7.6 | — | fide-2024 | IMPLEMENTED |
| STD | Standard Points | 7.7 | — | fide-2026 | IMPLEMENTED (standard scoring; exotic tables need score-model extension, U6) |
| SB + /C1 /C2 /P (+ combos) | Sonneborn-Berger | 9.1 | C1 C2 P | fide-2024 (+SB-C1) + fide-2026 | IMPLEMENTED (C1, C2, /P flag) |
| ARO + /C1 /C2 /M1 /M2 | Average Rating of Opponents | 10.1 | C1 C2 M1 M2 | fide-2024 (+C1) + fide-2026 | IMPLEMENTED (C1, C2, M1, M2) |
| TPR | Tournament Performance Rating | 10.2 | — | fide-2024 | IMPLEMENTED |
| PTP | Perfect Tournament Performance | 10.3 | — | fide-2024 | IMPLEMENTED |
| APRO | Avg TPR of Opponents | 10.4 | — | fide-2024 | IMPLEMENTED |
| APPO | Avg PTP of Opponents | 10.5 | — | fide-2024 | IMPLEMENTED |
| RTNG, RTNG/R | Rating | 10.6 | R | fide-2026 | IMPLEMENTED (descending terminal; /R consumer-side) |

Codes `SB/P`, `SB/C1/P`, `SB/C2/P`, `ARO/C1…`, `ARO/M1…` are listed
"to be implemented" — i.e. FIDE-mandatory once the base exists.

## Table 2 — both individuals and teams

| identifier | § | :MP/:GP | modifiers/options | implementation_status |
|---|---|---|---|---|
| WIN[:MP] | 7.1 | MP | — | IMPLEMENTED (individual; team use needs TeamMatch) |
| WON[:MP] | 7.2 | MP | — | IMPLEMENTED (individual; team dito) |
| PS[:MP/:GP] + /C1 /C2 | 7.5 | MP GP | C1 C2 | IMPLEMENTED (PS, PS-C1); PS-C2/… SPECIFIED |
| TPN, TPN/R | 7.8 | — | R | IMPLEMENTED (ascending terminal under fide-2026; /R consumer-side) |
| BH[:MP/:GP] + /C1 /C2 /M1 /M2 /P /F | 8.1 | MP GP | C1 C2 M1 M2 P F | IMPLEMENTED (individual BH/C1/C2/M1/M2; /P flag under fide-2026; /F-combos SPECIFIED) |
| AOB[:MP/:GP] + /F | 8.2 | MP GP | F | IMPLEMENTED (base + AOB/FB id `aob_fb` under fide-2026) |
| FB[:MP/:GP] + /C1 /C2 /M1 /M2 /P | 8.3 | MP GP | C1 C2 M1 M2 P | IMPLEMENTED (base FB + C1/C2/M1/M2 + /P flag under fide-2026) |
| KS[:MP/:GP] + /Lx | 9.2 | MP GP | Lx | IMPLEMENTED (base); limits SPECIFIED |

## Table 3 — teams only

| identifier | § | modifiers/options | implementation_status |
|---|---|---|---|
| BC | 12.1 | — | OUT_OF_SCOPE (team module) |
| TBR | 12.2 | — | OUT_OF_SCOPE |
| BBE | 12.3 | — | OUT_OF_SCOPE |
| MPvGP | 13.1 | — | OUT_OF_SCOPE |
| EMMSB/EMGSB/EGMSB/EGGSB + /C1 /C2 /P | 13.2.1–4 | C1 C2 P | OUT_OF_SCOPE |
| EDE + /P | 13.3 | P | OUT_OF_SCOPE |
| EDEBT/EDEBB/EDET/EDEB (+/P) | 13.3+13.3.2 | P | OUT_OF_SCOPE |
| SSSC + /F /P /Kx (+combos) | 13.4 | F P Kx | OUT_OF_SCOPE |

## Distinction (§5 of the mission) applied to MTB26

- **FIDE-defined**: every acronym above (formula in C.07).
- **FIDE-listed**: all Table 1–3 rows + every code in the code table
  (including generic `/Cn /Mn /Lx /Kx` instantiations).
- **Mandatory for approval**: the full code table ("tie-breaks that
  an endorsed program must implement"; `x` = any reasonable value).
  Approval attaches to a complete THP (see `FIDE_APPROVAL_PATH.md`),
  never to this library alone.
- **Optional tournament criterion**: any listed code the organiser
  does not select; plus `OTHER_*` self-defined (C.07 §4.1).
- **Consumer-owned**: which descriptors fill TRF 202/212 and in what
  order (organiser/arbiter; pre-tournament publication).
- **Out of library scope**: all Table-3 team codes + team
  instantiations of Table-2 codes (need TeamMatch domain).

Formula sources: `FIDE_CRITERIA_CATALOG.md` (individual),
`FIDE_TIEBREAK_MODIFIERS.md` (all `/…` variants). Required inputs per
code: base inputs from the catalog + `:MP/:GP` (team match scores) +
variant inputs (cut counts; Koya half-point shifts; SSSC divisor;
forfeit-inclusion flag; FB projection).

## Descriptor → core-request boundary (normative for adapters)

The core never parses TRF syntax. Consumer-owned normalization maps
each ordered descriptor to a calculation request:

```text
MTB26/TRF descriptor  →  consumer parsing  →  normalized core request  →  tiebreak-core
"BH/C1/P"             →  base BH + Cut-1    →  criterion "buchholz_cut1" (+ forfeit-inclusion flag, live under fide-2026 since 0.7.0)
"ARO/M2"              →  base ARO + Median-2 →  criterion "aro_median2" (fide-2026)
"DE/P"                →  base DE + forfeit-inclusion → positional "direct_encounter" stage (Swiss default; regulations opt-in via the fide-2026 flag since 0.7.0)
"OTHER_x"             →  NOT a FIDE criterion, never silently mapped; consumer resolves or the strict
                         core raises UnknownCriterionError on calculation request (legacy: frozen 0.0)
"BH:GP/C1"            →  team reference score → future team module (today: out of scope, explicit error)
```

Rules: modifiers are semantic (cut counts, flags, team-score refs),
never opaque strings inside the core; descriptor ORDER stays
consumer-controlled (the `criteria` list order); `PTS` (record 212)
means "primary points first", i.e. points-descending before the
listed codes — the core's standing comparator already orders by
points first. Unknown criteria: strict → typed error; legacy →
frozen `0.0` (never change). No broad API redesign needed: the
contract is ids + flags, and future flags (forfeit-inclusion,
mode) are additive strict parameters.
