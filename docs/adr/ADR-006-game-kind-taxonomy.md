# ADR-006: Explicit game-kind taxonomy (Phase 1)

Status: accepted (2026-10-03).

## Context

Legacy inputs conflate every unplayed/missing game into `opponent_id == -1`
(pairing byes, forfeit results, requested byes, absent opponents). FIDE
C.07 Article 16 assigns these different categories with different
arithmetic, so the conflation blocks any FIDE-correct ruleset.

## Decision

- Add an explicit `GameRecord.kind` vocabulary: `played`,
  `pairing_bye`, `forfeit_win`, `forfeit_loss`, `requested_bye`,
  `unplayed` (legacy generic), `absent`. See `GAME_KINDS`.
- The field defaults to `""` (unspecified) so all existing positional
  constructors keep working. `normalize_kind()` resolves unspecified to
  `unplayed` for `-1` and `played` for real opponents — old inputs keep
  their exact meaning; nothing is relabeled as FIDE-categorized.
- Deliberately NOT modeled: a separate withdrawal kind (post-withdrawal
  rounds are `requested_bye` with score 0.0 per §16.1.1; withdrawal
  itself stays a caller-side player fact), and early-vs-trailing
  requested-bye distinction (positional data, not a kind).
- Forfeit results may carry a real (scheduled) opponent or `-1`;
  bye-like kinds require `-1`; explicit `played` requires a real
  opponent. Enforced on the strict path only.
- Legacy calculators ignore `kind` entirely (frozen). Phase-2
  calculators will branch on it; until then kind-aware inputs compute
  legacy values, proven by tests.

## Consequences

- Impossible to accidentally treat a categorized unplayed game as an
  ordinary played game on the strict path; legacy path byte-identical.
