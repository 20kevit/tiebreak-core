# ADR-007: fide-2024 engine scope and naming

Status: accepted (2026-10-03).

## Context

The mission roadmap named the first FIDE-correct ruleset `fide-2026`.
Retrieval attempts showed: (a) the March-2026 C.07 full text is not
machine-retrievable (only index + excerpts); (b) the August-2024 C.07
full text IS retrieved (FIDE Council doc 2024_FC2_18, 653 lines).

## Decision

- Implement the engine as ruleset **`fide-2024`**, sourced exclusively
  from the fully-retrieved 2024 text. Keep **`fide-2026` reserved**
  until the 2026 full-text diff is retrieved and reviewed.
- Rationale: a ruleset id is a provenance claim (§40: never fake
  completeness). Naming the 2024-sourced engine `fide-2026` would assert
  unverified 2026 conformance. The ruleset model (ADR-001) supports
  multiple ids, so a future `fide-2026` can supersede or alias without
  disturbing `fide-2024` results.
- Scope of `fide-2024`: individual Swiss only. Included: Art.16
  categories/adjusted scores/dummy rule/cut exception, Cut/Median
  modifiers, SB-C1/PS-C1/ARO-C1, AOB, Fore Buchholz, OTB Type-B
  semantics, gap-filled Progressive, Koya on maximum-possible threshold.
  Excluded with reason: team systems (different domain objects),
  TPR/PTP/APRO/APPO (rating conversion tables not retrieved),
  Direct Encounter (needs group-context ranking — roadmap Phase 3),
  Art.16.6 local overrides (competition-regulation input, no contract).
- Same criterion ids as legacy where FIDE defines the same system; the
  ruleset namespaces the semantics. Per-id semantic deltas are recorded
  in `docs/TIEBREAK_RULES.md`; `REDEFINED_IDS` in `fide2024.py` lists
  ids whose meaning changed.

## Consequences

- Honest provenance at the cost of a less fashionable ruleset name.
  Chess-manager adoption should select per-tournament; historical events
  stay on `legacy-0.1.0`.
