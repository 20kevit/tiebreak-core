# Known limitations and explicit scope boundaries

Items 1–11: legacy (`legacy-0.1.0`) behavior — CURRENT BEHAVIOR, NOT
FIXED (frozen). Items 12–16: `fide-2024` explicit scope boundaries.

Each item: CURRENT BEHAVIOR → KNOWN LIMITATION → NOT FIXED IN v0.1.0.

1. FIDE Art.16 unplayed-round management — CURRENT: all unplayed games use
   `max(0, points - score)` (Buchholz/SB/Koya) or own rating (ARO).
   LIMITATION: no Art.16 categories, no draws-forth virtual opponent, no
   Cut-1 exception. NOT FIXED (needs new rules version).
2. Koya on Swiss — CURRENT: applied to Swiss with threshold
   `current_round / 2`. LIMITATION: FIDE §9.2 specifies round-robin.
   NOT FIXED. Phase 0 finding: chess-manager passes
   `tournament.current_round` (rounds played so far) where the
   calculator semantically expects total rounds. Same position yields
   e.g. Koya 2.5 at current_round=2 vs 0.0 at total_rounds=5 (values
   converge once current_round == total_rounds; mid-tournament display
   only). Correction deferred to the future `fide-2026` path.
3. Direct Encounter stub — CURRENT: `calculate_all(..., "direct_encounter")`
   returns `0.0`; `direct_encounter()` is a single-game lookup needing an
   explicit opponent. LIMITATION: not a FIDE §6 mini-league. NOT FIXED.
4. Simplified ARPO dp table (17 rows) — CURRENT: coarse thresholds.
   LIMITATION: diverges from FIDE conversion table; no unrated-drop rule.
   NOT FIXED.
5. Median edge — CURRENT: `<3` games falls back to full Buchholz.
   LIMITATION: undocumented vs FIDE; preserved. NOT FIXED.
6. Coronate mapping — CURRENT (chess-manager): parser maps to
   `median_system/solkoff/...` keys absent from the registry; generator
   hardcodes its own list. LIMITATION: dead/wrong mapping, lossy round-trip.
   NOT FIXED (out of core scope; adapter must not rely on it).
7. Crosstable sort divergence — CURRENT (chess-manager): crosstable sorts by
   `(-points, -rating)`, not the tie-break chain. LIMITATION: differs from
   standings. NOT FIXED (presentation concern).
8. Unused legacy `TiebreakResult` — CURRENT: defined, never used. KEPT for
   compatibility; new code should use `PlayerResult/StandingsResult`.
9. Rounding-before-ranking — CURRENT: ranking sorts ROUNDED values (BH 1dp,
   SB 2dp, ARO int). LIMITATION: borderline ties decided on rounded values.
   NOT FIXED (changing it would break equivalence).
10. Silent unknown criteria (legacy) — CURRENT: `calculate` returns `0.0`
    for unknown ids. LIMITATION: masks configuration typos. NOT FIXED on
    the legacy path (frozen); the additive strict path raises
    `UnknownCriterionError` instead.
11. Mutable legacy registry — CURRENT: `calculators.TIEBREAK_REGISTRY`
    remains a mutable global for compatibility. LIMITATION: importers can
    corrupt it. NOT REMOVED; new code must read via `frozen_registry()`
    and extend via `register_criterion()` (built-in overwrite refused).

## fide-2024 boundaries (explicit scope, not defects)

12. Team systems (§§11–13) — not modeled (different domain objects:
    matches, boards, MP/GP). Requested only if a team consumer appears.
13. TPR/PTP/APRO/APPO (§§10.2–10.5) — IMPLEMENTED under fide-2024
    from the fully-extracted official §§8.1a/8.1b tables (101 + 51
    entries, verified). Documented interpretations: p rounded half-up
    to hundredths; PTP target = OTB points; TPR built on rounded ARO.
14. Direct Encounter (§6) — IMPLEMENTED under fide-2024 as a
    group-level ranking stage (see ADR-008). Legacy standings-level
    value remains a 0.0 stub (frozen).
15. Art.16.6 local overrides — no competition-regulation input contract;
    unsupported by design until a consumer requires it.
16. March-2026 edition — the engine implements the fully-retrieved 2024
    text as ruleset `fide-2024`; `fide-2026` is reserved but now fully
    SPECIFIED (verified word-diff D1–D15 in `docs/FIDE_2026_DIFF.md`,
    corpus PENDING shells in `tests/corpus/fide2026_unplayed.json`,
    build order in `docs/IMPLEMENTATION_ROADMAP.md`). No `fide-2024`
    output changes with the 2026 specification (proven by the suite).
