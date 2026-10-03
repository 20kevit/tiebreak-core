# Conformance corpus — schema and status taxonomy

Machine-readable cases live next to this file (`*.json`).
`tests/test_corpus.py` loads and runs them.

## Case fields

| Field | Meaning |
|---|---|
| `id` | stable unique case id |
| `ruleset` | ruleset the expectation applies to |
| `status` | `VERIFIED` / `CROSS_CHECKED` / `PENDING` (below) |
| `source` | where the expectation comes from (URL/title/date) |
| `source_grade` | `PRIMARY` (official FIDE) / `SECONDARY` / `UNVERIFIED` |
| `article` | FIDE Handbook article/section (e.g. `C.07 §8.1 BH`) |
| `players` | `{id: {rating, points, games: [...]}}`; game = `{opponent, score, color, round, rating, kind?}` (`kind` from `GAME_KINDS`, default `""` = unspecified) |
| `criteria` | criteria to evaluate |
| `total_rounds` | rounds argument (Koya/context) |
| `expected` | `{player_id: {criterion: value}}` (absent for PENDING) |
| `notes` | interpretation notes, ambiguity records |

## Status taxonomy

- `VERIFIED` — expectation derived from an official FIDE source AND
  hand-computed independently of this library. Run as assertions.
- `CROSS_CHECKED` — expectation cross-checked against a trusted oracle
  (e.g. MIT-licensed reference implementation vectors). Run as
  assertions; the oracle is a cross-check, never the authority.
- `PENDING` — case shell for specified-but-unimplemented behavior
  (e.g. `fide-2026` Article 16, full Direct Encounter). Schema-validated
  only; execution is skipped until implementation lands. PENDING cases
  must never be silently treated as passing.

## Rules

- Never invent expected values. Every number traces to a source or an
  independent hand computation recorded in `notes`.
- Fully-played events (no unplayed games) are FIDE-version-agnostic for
  the basic definitions (BH/SB/PS sums); such cases may be VERIFIED
  against any C.07 edition's definition article.
- Cases involving unplayed games are version-sensitive: they MUST name
  the exact ruleset/edition and stay PENDING until that ruleset is
  implemented.
