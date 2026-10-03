# FIDE format variants (Swiss / RR / team / knockout)

## Swiss (individual)

Full C.07 Arts 6–10 + 14 + 16. Unplayed: Art 16 (categories, adjusted,
dummy+caps, VUR cuts). DE §§6.1–6.3 with certainty rule. BH-family
allowed (2026 RR-ban does not touch Swiss). Rating TBs drop with
unrateds unless pre-published handling. `fide-2024` implements this;
`fide-2026` specified. Status: IMPLEMENTED/SPECIFIED.

## Round-robin (individual)

- BH-family **must not be used** (2026 Art-8 note; 2024 merely
  useless-by-construction — all tied players share opponents).
- Forfeits (only possible unplayed): 2024 = regular games (§15.2);
  2026 = regular **except** forfeits excluded from §10 sets and
  forfeit losses excluded from Type-B counts (D12). No dummy rule
  (Art 16 is Swiss-only). Koya is RR-scoped (§9.2). DE: full meeting
  expected; §6.3 certainty inapplicable; forfeit inclusion still
  needs the §6.1.1 opt-in text. Status: SPECIFIED (RR mode flag is
  P1; no RR engine yet — correct, since Swiss is the implemented
  scope).

## Pre-determined pairings (generalisation of RR rule)

§15.2 as above. Applies to RR + any pre-paired format.

## Team Swiss

Arts 11–13 + 16 (team reading: "points" = MP and GP). MP/GP
primitives; ESB/EDE/SSSC/MPvGP; BC/TBR/BBE knockout codes;
2026 EDE chains. Unplayed-team-round handling per 16.x team notes.
Status: OUT_OF_SCOPE (TeamMatch domain).

## Team knockout (tied MP and GP)

§12 codes only (BC/TBR/BBE), forfeit wins/losses = standard,
PAB = standard-win GP per board (§12 intro). Invoked via §13.3.2
chains. Status: OUT_OF_SCOPE.

## Knockout/elimination (individual)

C.07 covers individual KO only via play-offs (Art 3), not
tie-break values. No BH/SB semantics defined — out of scope by
absence (recorded, not assumed).

## Rapid/blitz/alternative scoring

No separate formulas (WRBC: BH-C1→BH→AROC1→DE→lots, all "as
described in C.07"). Alternative scoring (3-1-0 etc.) is bridged by
STD (§7.7); TRF26 record 013 carries the event scoring table
(W/D/L/A/P/X + points). Armageddon decides matches, never feeds
tie-break inputs. Status: STD SPECIFIED; rest CONSUMER_OWNED.

## Pairing-time (C.04, not standings)

C.04 §§1.7–1.8 opposition evaluation (current scores, self-game,
acceleration exclusion; bracket order BH→SB→TPN) belongs to
pairing-core. Names collide with C.07; namespaces must not.

## ETT26 → regime mapping (consumer-owned)

| 192 code family | C.07 regime | tie-break consequences |
|---|---|---|
| FIDE_DUTCH_*, FIDE_DUBOV, FIDE_BURSTEIN, *_SWISS, FIDE_TEAM_*SWISS | Swiss (individual/team) | Art 16; BH allowed; DE §§6.1–6.3 |
| BERGER_*ROUNDROBIN, FIDE_*ROUNDROBIN (incl. team) | predetermined pairing | §15.2 (2026 carve-out); BH-ban; Koya home |
| SCHILLER / SCHEVENINGEN | predetermined (order/colour rules "not yet defined") | same as RR; rules pending are flagged NON-BLOCKING (no core input depends on them) |
| *KNOCKOUT | play-off (Art 3) / team §12 | individual: no tie-break values defined; team: BC/TBR/BBE chains |
| CUSTOM_* | organiser-defined | explicit `OTHER_*` mapping; NO silent inference from unrelated input |

The final architecture makes format selection explicit via a mode flag;
the adapter (never the core) owns 192 parsing + ETT26 lookup.
