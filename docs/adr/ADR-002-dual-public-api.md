# ADR-002: Dual public API — frozen legacy surface + strict surface

Status: accepted (2026-10-02).

## Context

The legacy surface (`calculate`, silent `0.0` for unknown criteria, mutable
global registry) is depended upon by chess-manager production standings.
Its lenient behaviors are load-bearing for compatibility but poor contracts
for new consumers.

## Decision

- Keep the legacy surface with frozen semantics (no strictening, no
  signature changes that alter outputs).
- Grow all fail-fast contracts on the additive strict surface
  (`tiebreak_core.strict`): typed errors, input validation, explicit
  `ruleset=` selection. Strict delegates to legacy implementations, so
  values are identical by construction, proven by equivalence tests.
- Internal layering: `models` (data) → `calculators` (pure functions) →
  `ranking` (pure ordering) → `strict` (validation boundary). `display`
  stays outside the calculation path.

## Consequences

- Existing callers never break; new consumers get real contracts. The
  cost is two documented surfaces instead of one — justified by the
  frozen-compatibility requirement.
