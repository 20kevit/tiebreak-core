# FIDE tie-break master specification (tiebreak-core)

Authoritative map of the FIDE tie-break domain as researched
2026-10-03. Every normative claim traces to a PRIMARY source in
`FIDE_SOURCES.md`; SECONDARY material is labeled; gaps are in the
uncertainty register (`IMPLEMENTATION_ROADMAP.md`), never hidden.

1. **What FIDE defines**: C.07 Play-Off and Tie-Break Regulations —
   ranking methods (OTB play-offs Art 3; off-board ordered tie-break
   lists Art 4), criterion taxonomy Types A/B/C/D-combos (Art 5 table),
   individual criteria (Arts 6–10), team criteria (Arts 11–13),
   modifiers (Art 14), unplayed-round regimes (Arts 15–16). Full
   inventory: `FIDE_RULE_INVENTORY.md`; catalog:
   `FIDE_CRITERIA_CATALOG.md`.
2. **Rulesets**: pre-2023 (till 31 Aug 2023) → Sep-2023 → Apr-2024
   (clarifications) → Aug-2024 (to 28 Feb 2026) → Mar-2026 (current).
   History: `FIDE_RULESET_HISTORY.md`. Package rulesets:
   `legacy-0.1.0` (frozen), `fide-2024` (implemented), `fide-2026`
   (implemented since 0.7.0: Swiss core + RR mode + terminals;
   STD/C2-combos since 0.8.0).
3. **Criteria**: 29 individual scalars + DE group stage + TPN/RTNG
   terminal stages implemented (fide-2026; fide-2024 covers its era
   subset); team out-of-scope. See catalog.
4. **Inputs per criterion**: `FIDE_CRITERIA_CATALOG.md` (formula +
   required/optional) and `FIDE_DATA_SEMANTICS.md` §4 (model gaps).
5. **Calculations**: catalog formulas; Article 16: `fide2024.py`
   `classify/adjusted_score/dummy/cuts` + dependency matrix (data
   semantics §3).
6. **Unplayed games**: five categories (16.2), VUR, adjusted scores
   (16.3), dummy (16.4: uncapped 2024 / capped 2026), cut exception
   (16.5), RR regime (15.2, 2026 carve-out), opt-out (16.6, deferred).
7. **Missing data**: `FIDE_DATA_SEMANTICS.md` §1 — valid zero vs
   typed failure; never `missing == 0` without article basis.
8. **Direct Encounter**: catalog §DE + ADR-008 — mini-standings,
   forfeit scope, averaging, §6.2 reapplication, §6.3 certainty,
   guaranteed termination; group stage, no scalar.
9. **Recursive ranking**: successive criteria per still-tied subgroup
   (Art 4.2, 2026 wording) composed by `rank_standings[_strict]` over
   explicit ordered lists; DE re-enters positionally (Type A
   multi-listable). No separate engine needed.
10. **Sequencing**: caller-owned ordered lists (Art 4.1), arbiter
    completion pre-tournament; exhausted list → lots (consumer).
11. **Precision**: data semantics §2 — exact sums; half-up once at
    ARO/APRO/APPO/AOB; TPR hundredth-rounding + tables; PTP full
    scale; legacy rounding frozen.
12. **What changed**: `FIDE_2026_DIFF.md` (D1–D15; only semantic
    deltas: subgroup wording, STD/TPN/RTNG, RR-ban note, AOB-FB note,
    first-rating rule, EDE chain names, §15.2 carve-out, §16.4 caps,
    examples annex) + history chapter.
13. **tiebreak-core ownership**: individual calculations, Art 15/16,
    DE stage, rating values, ranking composition, ruleset pins.
14. **Consumer ownership**: lists, seeding, filtering, snapshots,
    presentation, pairing-time C.04 quantities (pairing-core),
    persistence (manager). Full split: `ARCHITECTURE_GAP_ANALYSIS.md`.
15. **Uncertainties**: roadmap register (8 items, all bounded).
16. **Before 1.0**: roadmap §1.0 — fide-2026 Swiss core + corpus
    green + adoption + perf budgets.
17. **Optional/future**: Koya-limit machinery, 16.6 overrides, team
    module (on demand), AOB-FB variant, norm-TPR (never in core).

Tournament classification: ETT26 (C.02.03 Annex C) maps TRF field 192 to the format regime
(Swiss/RR/team/knockout/custom) — consumer-owned lookup; see `FIDE_FORMAT_VARIANTS.md`.

Research provenance: `FIDE_SOURCES.md`. Software context (never
normative): `SOFTWARE_COMPARISON.md`. Conformance method:
`FIDE_CONFORMANCE_PLAN.md`. Build order:
`IMPLEMENTATION_ROADMAP.md`.
