# FIDE evaluation dossier — `tiebreak-core`

English-language dossier for an initial inquiry to the FIDE Technical
Commission (TEC). Prepared 2026-10-27. It states what the product is,
what it is not, what it implements, how conformance is evidenced, and
what remains open. It contains **no claim of FIDE approval,
certification, endorsement or acceptance**.

---

## 1. Product

| | |
|---|---|
| Name | `tiebreak-core` |
| Version | **1.3.0** (unreleased; last published release is **1.2.0**, 2026-10-04) |
| Repository | `https://github.com/20kevit/tiebreak-core` |
| Language / runtime | Python ≥ 3.10, pure Python, **zero runtime dependencies** |
| License | MIT |
| Package | `tiebreak-core` on PyPI (sdist + wheel) |

## 2. Precise statement of scope

`tiebreak-core` is a **standalone tie-break calculation library**. It
takes normalized tournament data as input and returns tie-break values
and tie-break rankings. It is **not** a Tournament Handler Program and
does not claim that product category.

**In scope**

- Individual-player tie-break calculations (scalar values).
- Team tie-break calculations to the extent defined by C.07 §§11–13.
- Ordered tie-break ranking and tie resolution where the documented API
  includes it.
- Official rank-order descriptors (the MTB26 grammar), their supported
  combinations, modifiers, options and validation.
- Interpretation of game results, forfeits, unplayed rounds, byes,
  opponents, ratings, scores, colours, boards and other inputs.
- Strict input validation, deterministic calculation, reproducibility,
  tests, documentation and conformance evidence.

**Explicitly out of scope**

- Swiss pairing generation or pairing repair.
- Tournament administration, registration, player management, lifecycle.
- Tournament file import/export (TRF, ETT, RTG, PTC workflows).
- User interfaces, websites, databases, APIs for tournament-management
  applications, application orchestration.
- Rating calculation, chess engines, game adjudication.
- Changes to sibling repositories or consuming applications.

Consuming applications own pairing, file I/O, persistence and the TRF
202/212 descriptor lists. The library parses the **MTB26 rank-order
descriptor grammar** semantically but never parses TRF record syntax.

## 3. Intended use and evaluation category

- **Intended use:** a reusable, embeddable calculation core for
  tournament-management software, arbiter tooling and conformance
  testing — i.e. the calculation component a Tournament Handler Program
  would embed.
- **Intended evaluation category:** a **calculation library**, evaluated
  on its calculation conformance against the applicable FIDE
  regulations. It is **not** submitted as a complete THP: a THP must
  additionally cover pairing, TRF26 202/212 emission, PTC/RTG CLIs,
  ITDX, Acceptance Cycles and large-scale differential verification
  (see `docs/FIDE_TEC_IMPLEMENTATION_REQUIREMENTS.md`).

## 4. Rulesets implemented and effective dates

| ruleset id | FIDE text | Approved | Effective | Reproducibility |
|---|---|---|---|---|
| `legacy-0.1.0` | pre-2023 legacy calculators | — | frozen | byte-identical, pinned by `tests/data_goldens.json` |
| `fide-2024` | C.07 effective 1 Aug 2024 – 28 Feb 2026 | 29/07/2024 | 1 Aug 2024 | frozen engine; descriptor dispatch added in 1.3.0 |
| `fide-2026` | C.07 effective 1 Mar 2026 | 02/02/2026 | 1 Mar 2026 | current; **latest applicable edition** |

The current applicable regulations for the target scope are the
**C.07 edition effective 1 March 2026** (retrieved in full, 2026-10-27;
see `docs/FIDE_SOURCES.md` item 15). The Handbook C.07 index lists no
edition after 032026.

## 5. Conformance matrix and verification methodology

Full rule-by-rule mapping: `docs/FIDE_COMPLETE_REQUIREMENTS_MATRIX.md`.
Descriptor-by-descriptor coverage against the TEC **Mandatory
Tie-Breaks** tables: `docs/FIDE_MTB26_CATALOG.md`. Rule inventory:
`docs/FIDE_RULE_INVENTORY.md`. Interpretation register:
`docs/FIDE_DATA_SEMANTICS.md`, `docs/FIDE_TIEBREAK_MODIFIERS.md`.

Methodology

1. **Authoritative text.** C.07 retrieved in full for 2023, 2024 and
   2026; the TEC Mandatory Tie-Breaks descriptor specification; the TEC
   Tie-Break Exercises; the FIDE Technical Commission Manual.
2. **Official worked examples.** `docs/FIDE_OFFICIAL_EXAMPLES.md` maps
   every applicable official example to a test or a documented gap.
3. **Hand-computed fixtures.** Small coherent tournaments whose expected
   values are derived by hand from the regulations, not from the
   implementation.
4. **Differential / property tests.** Cross-ruleset divergence tests,
   exhaustive permutation sweeps, and input-order invariance.
5. **Regression tests for every discovered defect**, each failing
   before the fix and passing after.

## 6. Reproducible installation and test instructions

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .
python -m pytest -q                 # 743 passed, 69 documented skips, 0 failed
python -m pytest tests/test_examples.py -q   # examples A–G
python -m build                     # sdist + wheel
```

Clean-install check (no editable path):

```bash
pip install dist/tiebreak_core-1.3.0-py3-none-any.whl --target /tmp/x
PYTHONPATH=/tmp/x python -c "import tiebreak_core as t; print(t.__version__)"
```

Environment: Python 3.10–3.12, pytest; no runtime dependencies.

## 7. API and representative examples

```python
from tiebreak_core import (PlayerTiebreakData, GameRecord,
                           calculate_all_strict, rank_standings_strict,
                           calculate_descriptor_strict)

pl = {1: PlayerTiebreakData(1, 2000, 3.0,
                            [GameRecord(2, 0, 1.0, "white", 1, "played")]),
      2: PlayerTiebreakData(2, 1900, 0.0,
                            [GameRecord(1, 0, 0.0, "black", 1, "played")])}

# Named criteria under a ruleset
calculate_all_strict(pl[1], pl, ["buchholz", "buchholz_cut1", "koya"],
                     1, ruleset="fide-2026")

# Rank-order descriptors (MTB26 grammar)
calculate_descriptor_strict(pl[1], pl, "BH/C1/P", 1, ruleset="fide-2026")
rank_standings_strict(pl, ["buchholz"], 1, ruleset="fide-2024")
```

Full surface: `docs/API.md`.

## 8. Known limitations and unresolved interpretations

Full register: `docs/KNOWN_LIMITATIONS.md`. Highlights:

- `legacy-0.1.0` is a frozen legacy ruleset with documented divergences
  from current FIDE semantics. It is preserved for reproducibility and
  is **not** a conformance claim.
- `fide-2024` implements Swiss scope (Article 16). It has no
  round-robin mode; round-robin scope belongs to `fide-2026`.
- `fide-2026` round-robin `AOB`/`AOB-F` count only over-the-board
  opponents (`kind == played`). §8.2 says "played over the board" while
  §15.2 says round-robin forfeits are regular games — a genuine
  ambiguity, **left unchanged** and registered rather than guessed.
- Standard Points (§7.7) supports the standard 1–½–0 scoring; exotic
  scoring tables require explicit per-round `opponent_score` values
  (organiser contract).
- Koya (§9.2) is scoped by FIDE to round robin; the implementation
  applies it wherever requested.
- `/M1` across descriptor families is read as "cut the least
  significant value" (§14.3 name-form mismatch in the official text).

## 9. Contact points and questions for the FIDE Technical Commission

- **TEC contact (verified from the FIDE announcement of 2026-04-02):**
  Hendrik du Toit — `secretary.tec@fide.com`.
- **TEC Manual:** `https://tec.fide.com/fide-technical-manual/`.
- **Tie-break category:** `https://tec.fide.com/category/tie-break/`.

Questions for written confirmation

1. Does a **standalone calculation library** have an evaluation route
   distinct from the THP route, or must it be submitted as part of a
   complete Tournament Handler Program?
2. Is Technical Acceptance of Product Compliance (TAPC) the applicable
   procedure for a calculation component, and does it accept a
   component-level submission?
3. Is there a conformance checklist covering tie-break calculation
   software specifically, and is an external test suite available?
4. The TEC has stated tie-break/standings TAPC testing starts "for the
   first time in the future". Which acceptance cycle will first include
   tie-breaks, and what is the submission window?
5. Confirmation of the round-robin `AOB` forfeit-opponent scope
   (§8.2 "played over the board" vs §15.2 "regular games").
6. Confirmation of the `/P` cross-reference in the Mandatory Tie-Breaks
   document ("Article C.07.16.5", which is the Cut-1 exception in every
   edition).

## 10. Evidence that can be supplied to reviewers

- Full test suite and skip map (69 documented differential skips).
- Rule-by-rule conformance matrix with article citations.
- Descriptor coverage matrix against the TEC Mandatory Tie-Breaks
  tables, with per-descriptor status.
- Regression tests and before/after values for every corrected defect
  (R1 ruleset dispatch, R2 round-robin REP, R3 `/P` under `fide-2024`).
- Hand-computed fixtures and official-example traceability.
- Clean sdist/wheel, CI workflow, and build logs.

## 11. Procedural items — status

| Item | Status |
|---|---|
| Product classification for a calculation library | **Requires FIDE confirmation** (question 1) |
| Applicable procedure (TAPC / other) | **Requires FIDE confirmation** (question 2) |
| Required forms, declarations, fees | **Not verified from an official source for this product category** — no form, fee or route is asserted here |
| Conformance checklist for tie-break software | **Requires FIDE confirmation** (question 3) |
| Official test suite / external tester | **Requires FIDE confirmation** (question 4) |
| Online application route | To be confirmed with TEC on inquiry |

Nothing in this dossier constitutes an application, a payment, a
declaration, or a claim of approval. No submission has been made.

## 12. Terminology used in this dossier

- "Implemented against the applicable FIDE regulations" — supported by
  the cited article and test evidence.
- "Technically verified within the documented scope" — the verification
  evidence in §5 justifies it.
- "Prepared for formal evaluation" — this dossier is complete.
- "FIDE accepted / certified / endorsed" — **not claimed**. No such
  status has been granted or independently verified.
