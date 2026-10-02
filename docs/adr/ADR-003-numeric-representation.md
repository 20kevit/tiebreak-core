# ADR-003: Numeric representation (floats with documented rounding)

Status: accepted (2026-10-02).

## Context

Tie-break values involve halves (0.5) and sums/products thereof. Exact
decimal arithmetic (e.g. `Fraction`) would be ideal, but the frozen legacy
behavior uses binary floats with per-criterion rounding (Buchholz family
1dp, Sonneborn-Berger 2dp, ARO/ARPO integer via `round()`).

## Decision

- `legacy-0.1.0` keeps float arithmetic + documented rounding exactly as
  extracted. This includes Python banker's rounding in `round()` (pinned
  by `test_legacy_frozen.py`).
- Ranking sorts the ROUNDED values (part of the frozen contract).
- Future rulesets SHOULD prefer exact arithmetic internally (sums of
  halves are exact in binary floating point; products like SB terms are
  too — all FIDE inputs are multiples of 0.5 — but integer/dp rounding
  must be specified per criterion in the ruleset definition).
- Scores are validated as members of {0, 0.5, 1} on the strict path;
  non-finite values are rejected.

## Consequences

- No silent "precision improvements" to legacy outputs. New rulesets get
  a clean numeric spec from day one.
