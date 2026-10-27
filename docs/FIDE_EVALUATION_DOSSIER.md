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
python -m pytest -q                 # 982 passed, 69 documented skips, 0 failed
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

---

## Release-readiness audit — 2026-10-27

### Candidate

| | |
|---|---|
| Branch | `arena/0a162545-tiebreak-core` |
| Commit | `8ee180ef3fa3a82bef51a999b71a2f389b314818` |
| Ahead of `main` | 6 commits (`23e85ce`, `94f68f1`, `13bbac4`, `0f3adad`, `b4503a8`, `8ee180e`) |
| `main` | `61491321d7886ab4abe1b7c64686dfce48d2c3dd` |
| Tag `v1.2.0` | `a04f0f1` — **untouched** |
| Published PyPI | 1.2.0 only — **untouched** |
| Working tree | clean |

### CI evidence (actual remote run)

Run **`40526241856`** — https://github.com/20kevit/tiebreak-core/actions/runs/40526241856

| Job | Status |
|---|---|
| `test (3.10)` | **success** |
| `test (3.11)` | **success** |
| `test (3.12)` | **success** |
| `packaging` (build wheel+sdist, `twine check`, clean-install smoke tests) | **success** |

This is the first successful CI run in the repository's history. **Root cause of
every prior failure (including the five `main` runs):** the test job's only
install step was `pip install -e .`, and the project declares
`dependencies = []` with no optional-dependencies, so `pytest` was never
installed and the `Tests` step died with `No module named pytest`. Fixed by
adding a `dev` extra and installing `.[dev]` (commit `8ee180e`).

Two workflow gaps were also closed: the workflow triggered only on `main`
(commit `b4503a8`), so none of the audit commits had any CI coverage.

**Limitation:** per-job stdout could not be retrieved (`gh run view --log`
and the jobs-log API both return EOF in this environment). The job
*conclusions* above come from the GitHub API and are authoritative; the
per-version test totals were not readable from the log. Locally the same
suite reports **982 passed / 69 skipped / 0 failed** on Python 3.11.

### Skip accounting (69 = reported 69)

| Test | Count | Reason | Still relevant? | Condition to execute |
|---|---|---|---|---|
| `test_differential.py::test_edition_coincidence_fide2024` | 54 | 9 criteria × 6 fixtures: `aro_cut2`, `aro_median1/2`, `fore_buchholz_cut1/2`, `fore_median1/2`, `sonneborn_berger_cut2` are **fide-2026-only**, so there is no fide-2024 value to compare | Yes — documents a real ruleset boundary | None: the comparison is impossible by design; the criteria are absent from the 2024 registry |
| `test_differential.py::test_koya_fully_played_only` | 9 | Koya threshold basis diverges on bye-inflated scores (documented); fully-played events only; plus 2 `echecs` fixtures where Koya double-counts repeated meetings (RR-only scope) | Yes — documents a known divergence | Fully-played fixtures only; the `echecs` fixtures need a true round-robin |
| `test_differential.py::test_exact_agreement_fide2026` | 3 | Degenerate edge policy: core falls back to uncut ARO below 5 rated opponents, oracle yields 0 (both documented; unit-tested separately) | Yes | A fixture with ≥5 rated opponents |
| `test_conformance.py::TestOldVsNewLive::test_live_equivalence` | 3 | `chess-manager` repo not available | Yes — would be a genuine third-party cross-check | Clone the `chess-manager` reference implementation |

### v1.2.0 differential (published artifact vs candidate)

Harness: `tools/compat/probe_v120.py` + `tools/compat/run_differential.py`.
It installs the **actual published `tiebreak_core-1.2.0-py3-none-any.whl`**
(downloaded from PyPI into `/tmp/v120`) in one isolated venv and the current
checkout in another, runs an identical probe in each, and compares
canonicalized JSON. Artifacts: `/tmp/tiebreak-compat/{v120,cand,diff}.json`
and `diff.txt`.

**Scope limitation:** 193 cases covering every ruleset, all named criteria,
28 individual descriptors, 18 team criteria, Swiss/round-robin modes, the
`/P` flag and ranking paths. This is **not exhaustive** — it is a
representative regression corpus, not a proof of equivalence.

| Class | Count | Interpretation |
|---|---|---|
| `UNCHANGED` | 120 | Identical values, including **all four `legacy-0.1.0` cases** and **all 18 computable team criteria** |
| `UNCHANGED-ERROR` | 25 | Same error on both sides (criteria absent from the 2024 registry; signature differences) |
| `ERROR-CHANGE` | 21 | Message-only: R1 now names the *correct* ruleset (`fide-2024`) instead of always `fide-2026`; R3 removed `forfeits_as_played` from the fide-2026-only kwarg list |
| `RESTRICTION` | 9 | Intentional tightening: Article 8 (BH/AOB/FB in round-robins), R4 `/P` scope (AOB/KS), R1 descriptor scope (`AOB/F` under fide-2024) |
| `API-CHANGE` | 3 | R3: `forfeits_as_played` is now **accepted** under `fide-2024` for the BH/SB/FB families (previously rejected as a fide-2026-only kwarg) |
| `BEHAVIOUR-CHANGE` | 1 | **R2** — see below |

**The one published-ruleset behaviour change.**
`rr.fide-2026.rep_forfeit_loser`: `3.0` (v1.2.0) → `0.0` (candidate).
§7.6 defines REP as *"the number of rounds reduced by the number of
half-point-byes, zero-point-byes or **forfeit losses**"*; v1.2.0 did not
subtract forfeit losses. This changes `fide-2026`, a ruleset that **was**
present in v1.2.0. It is a deliberate, documented in-place correction
(see `CHANGELOG.md` R2 and `docs/VERSIONING.md`), packaged as a MINOR bump
to 1.3.0. It is **not** hidden by this report.

**No unexplained regression was found.**

### Team round-robin format (Article 8)

The team data model (`TeamRecord` / `TeamMatch` / `TeamFormat`) has **no
tournament-format field**. `TeamFormat` carries only scoring parameters
(`mp_win`, `mp_draw`, `max_gp_per_match`).

Design taken (commit `0f3adad` + this audit): an explicit `mode` parameter
on `strict.calculate_team_strict` / `rank_teams_strict`.

| `mode` | Meaning | Article 8 applied? |
|---|---|---|
| `None` (default) | Format **not declared** | No — and this is *not* treated as Swiss. Pinned by `tests/test_team_rr_scope.py::test_undeclared_format_does_not_apply_the_restriction`. |
| `"swiss"` | Swiss | No |
| `"round_robin"` | Round-robin | Yes |

Restricted bases: `BH`, `AOB`, `FB`, `SSSC` (SSSC because §13.4.2 defines
schedule strength as "Buchholz of the team"). **Not** restricted: ESB
(§13.2 — a Sonneborn-Berger variation, Article 9), EDE and its chains
(Article 6), KS (Article 9), BC/TBR/BBE (Article 12), MPvGP/WIN/WON/PS.

`tests/test_team_rr_scope.py` (84 tests) covers prohibited and permitted
combinations including `:MP`/`:GP` variants, `mode=None` semantics, and
invalid mode values. The raw `team.calculate_team` engine remains callable.

### Official-exercise coverage matrix

| Family | Status | Source | Test identifier |
|---|---|---|---|
| BH (Swiss) | **verified against an official worked example** | TEC *Tie-Break Exercises* (C.07-2023, Rev. 2403220900), Exercise 1 — `BH(#2) = 1.0+1.5+3.5+3.5+3.5 = 13.0` | `tests/test_official_examples_swiss.py` |
| BH-C1/C2, M1/M2 | verified against normative definition | C.07 §8.1 + §14 modifiers | `test_fide2026.py`, `test_modifiers.py` |
| AOB / AOB-F | verified against normative definition | C.07 §8.2 | `test_fide2026.py::TestAobExactRanking` |
| FB family | verified against normative definition | C.07 §8.3 | `test_fide2026.py::TestCutCombosAndAobFb` |
| SB family | verified against normative definition | C.07 §9.1 | `test_fide2026.py` |
| Koya (KS) | verified against normative definition | C.07 §9.2 | `test_fide2026.py::TestKoyaLimits` |
| ARO/TPR/PTP/APRO/APPO | verified against normative definition | C.07 §10.1–10.5 (conversion table per FIDE Rating Regulations) | `test_fide2026.py` |
| WIN/WON/BPG/BWG | verified against normative definition | C.07 §7.1–7.4 | `test_fide2026.py::TestStandardPoints` |
| PS / STD / REP / TPN / RTNG | verified against normative definition | C.07 §7.5–7.8, §10.6 | `test_fide2026.py`, `test_rr_rep_forfeit_scope.py` |
| DE / EDE / chains | verified against normative definition | C.07 §6.1–6.3, §13.3 | `test_team.py`, `test_fide2026.py` |
| Team ESB / SSSC / BC / TBR / BBE / MPvGP | verified against normative definition | C.07 §11–13 | `test_team.py` |
| `legacy-0.1.0` | **internally regression-tested only** (frozen) | — | `test_fide2024.py`, `test_differential.py` |

**Only one official worked example has been transcribed and verified
(Exercise 1).** The remaining TEC *Tie-Break Exercises* chapters (BH-C1,
AOB, FB, SB, Koya, ARO/TPR/APRO/PTP, DE, WIN/WON, BPG/BWG, GE/PS and the
team chapters) remain **unverified against worked examples**; they are
covered by normative-definition and regression tests only. The single
Buchholz check is **not** comprehensive coverage.

### Remaining blockers

1. **Official-exercise coverage is one value wide.** Only TEC Exercise 1 is
   independently verified. All other chapters are normative-definition or
   regression coverage.
2. **`test_live_equivalence` (3 skips) cannot run** — the `chess-manager`
   reference implementation is not available. This is the only remaining
   third-party cross-check.
3. **Team criteria are not ruleset-scoped.** `calculate_team_strict` /
   `rank_teams_strict` take no `ruleset`, so the Article-8 check applies
   regardless of ruleset. Under `fide-2024` (which has no Article 8 note)
   a team round-robin would still be refused. This is a **design gap, not
   a resolved item** — it needs a `ruleset` parameter on the team
   conformance entry points.
4. **R2 changes published `fide-2026` behaviour.** Documented and
   intentional, but anyone relying on v1.2.0's REP value for
   forfeit-losing players in round-robins sees a different number.
5. **CI per-job stdout unreadable** in this environment (EOF); only job
   conclusions are available.

### Verdict

**NOT READY** for preparing a release candidate.

The blocking item is #1: a release candidate cannot be justified while the
only independently verified official worked example is a single Buchholz
value, and the remaining mandatory descriptor families rest on
normative-definition readings rather than transcription of the official
exercises. Items #3 and #4 are additional unresolved design/compatibility
questions. Nothing here is a claim of FIDE approval, certification,
endorsement or acceptance — no such claim is made or supported.
