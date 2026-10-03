# ADR-001: Explicit ruleset model with frozen behavior pins

Status: accepted (2026-10-02).

## Context

Tie-break rules evolve (FIDE Handbook C.07 editions). Historical tournament
results must stay reproducible, while future FIDE-correct behavior must be
addable without breaking them.

## Decision

- Every calculation is stamped with the ruleset that produced it
  (`StandingsResult.rules_version`).
- Ruleset metadata is inspectable: `RulesetInfo` (id, status, description,
  FIDE reference, criteria) via `available_rulesets()` /
  `describe_ruleset()`.
- Statuses: `implemented` (calculable) vs `reserved` (name claimed,
  requesting it raises `UnsupportedRulesetError`).
- Status note (2026-10-03): the non-implemented state is now called
  `specified` (researched + specified, implementation pending) instead
  of `reserved`, per the development-readiness gate — same machine
  meaning (calculation refused), honest label. Code (`rules.py`) and
  tests updated accordingly.
- New behavior = new ruleset id + new code paths. Editing a frozen
  ruleset's outputs is forbidden (would be a MAJOR breaking change and a
  reproducibility violation).
- Package versions (semver) and ruleset versions are independent axes
  (see `docs/VERSIONING.md`).

## Consequences

- `legacy-0.1.0` stays byte-stable forever; `fide-2026` can land without
  touching it. Callers select rulesets explicitly; no "latest" drift.
