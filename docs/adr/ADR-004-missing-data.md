# ADR-004: Missing-data semantics

Status: accepted (2026-10-02).

## Context

Tournaments contain byes, forfeits, withdrawals, missing opponents, and
incomplete rounds. A single generic "treat as zero" rule is wrong for
different FIDE systems (cf. C.07 Article 16 categories).

## Decision

- `legacy-0.1.0` semantics are frozen and documented, not fixed:
  unplayed/missing games are one conflated `-1`/absent case substituting
  `max(0, points - score)` (Buchholz family/SB/Koya) or own rating (ARO);
  absent opponents are skipped; `points` is caller-accumulated.
- Distinctions the domain requires (valid zero vs missing vs not
  applicable vs invalid vs undefined) are enforced structurally:
  invalid shapes are rejected with typed errors on the strict path
  (`InvalidGameRecordError`, `InvalidPlayerDataError`); unknown criteria
  and rulesets are rejected (`UnknownCriterionError`,
  `UnsupportedRulesetError`).
- The future `fide-2026` ruleset MUST introduce an explicit unplayed-game
  taxonomy (bye kinds, forfeit win/loss, requested byes, withdrawals) as
  new input fields — never by reinterpreting `-1`.

## Consequences

- Legacy stays reproducible; the data model can grow the distinctions
  FIDE requires without breaking old inputs.
