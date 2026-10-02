# ADR-005: Registry — controlled extension without global mutable state

Status: accepted (2026-10-02).

## Context

Calculation dispatch needs a criterion-id → function mapping. A bare
mutable global invites accidental corruption and silent built-in
overwrites, yet the legacy `TIEBREAK_REGISTRY` dict is imported by
consumers and must keep working.

## Decision

- Keep the legacy dict object (compatibility), but make it a
  second-class citizen: new code reads via `frozen_registry()`
  (immutable snapshot) and extends via `register_criterion()`, which
  REFUSES built-in ids (`RegistryError`) and non-callables.
- `unregister_criterion()` removes custom ids only (built-ins refuse);
  primarily for test isolation.
- No dynamic package scanning, no auto-discovery, no plugin entry-point
  magic: registration is always an explicit call, auditable in code.
- Custom ids live in the same dispatch table (simple, single lookup);
  ruleset scoping of criteria (which criteria a ruleset offers) is
  metadata in `RulesetInfo.criteria`, enforced on the strict path via
  `require_criteria` + ruleset selection in later phases.

## Consequences

- Predictable, testable dispatch; thread-safety posture is "explicit
  registration at startup, frozen snapshots at use" (documented; no
  locks needed for the read path).
