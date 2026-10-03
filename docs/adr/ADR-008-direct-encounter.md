# ADR-008: Direct Encounter as group-level ranking stage (Phase 3)

Status: accepted (2026-10-03).

## Context

FIDE C.07 §6 defines Direct Encounter over *sets of tied participants*
(mini-standings, subset reapplication, Swiss conditional ranking). It
cannot be a per-player scalar: its inputs (the tied group) only exist
during ranking, and its output (ordered tiers) feeds subsequent criteria.

## Decision

- DE is a **ranking stage**, not a calculator. In `fide2024`
  `rank_standings`, criteria are applied as ordered stages over player
  groups: points first, then each scalar criterion splits groups by
  value, while `direct_encounter` resolves tied groups into ordered
  tiers (§§6.1–6.3). Unresolvable tiers fall through to later criteria;
  ultimate ties fall back to `deterministic_keys` (groups pre-sorted, so
  all stages are stable).
- Mini-table rules implemented: only `played` games between group
  members count; forfeit results excluded (Swiss scope, §6.1.1);
  repeated meetings contribute each side's average (§6.1.2, exact
  `Fraction` arithmetic — averages like 5/6 are not binary-exact).
- §6.2: all-met groups order by mini-score; tied subsets recurse
  (strictly shrinking → terminates; no-progress ties become one tier).
- §6.3: a player alone at top in *all* completions of unplayed pairs
  (mini-score strictly greater than every rival's score plus their
  maximum attainable remainder) ranks first, iteratively; the rest
  re-enters as one tier. "Unplayed pair" = no game record between them
  in either direction (documented interpretation: excluded forfeit pairs
  are fixed exclusions, not variable outcomes).
- Scalar `direct_encounter` is rejected under fide-2024
  (`UnsupportedCriterionError`): no per-player scalar exists. Standings
  `values` carry scalar criteria only (documented in API + ranking
  docstring).
- Legacy `direct_encounter` stub (0.0) is untouched.

## Consequences

- Criteria sequences mixing scalars and DE behave positionally, matching
  how FIDE multi-lists Type-A systems. Future group-level systems
  (e.g. team EDE) extend `GROUP_CRITERIA`, not the scalar registry.
