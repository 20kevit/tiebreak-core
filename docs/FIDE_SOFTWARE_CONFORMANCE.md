# FIDE software conformance (C.02 ecosystem)

## Framework (effective 1 Mar 2026)

Restructured C.02 (Congress-2026 paper + C.02.01 snippets, retrieved):
**C.02.01** General Regulations (definitions, VCL/SDPC/TAPC process,
revocation, fees) · **C.02.03** software (absorbed ex-C.04.A pairing
endorsement; THP = historically "pairing programs") · **C.02.04**
public register of accepted/endorsed equipment · TEC Manual (procedure,
never overriding the Handbook) · Acceptance Cycles (implementation
windows + common baselines).

## What FIDE considers a compliant program

A THP (7.4.10, incl. paper/admin systems with a handler) that:
declares via VCL+SDPC; passes TAPC (version-pinned, Council-approved);
implements all MTB26 codes; ships free PTC+RTG CLIs; survives 50k
differential verification; tracks Acceptance Cycles (rule-change
revocation); and — for *endorsement* — holds a commercial agreement
(TAPC ≠ endorsement, §7.7–7.8). Web THPs must be testable offline
(e.g. VM). "FIDE Endorsed" is the only marketing-safe claim
(C.02.01.2.9; "Acceptance" must not be used promotionally).

## What tiebreak-core itself can claim (and not)

- MAY claim: **FIDE-conformant / FIDE-aligned calculations** for the
  implemented rulesets (each value traceable to C.07 article + corpus
  case), **candidate calculation core** for a THP's TAPC submission,
  file-transparent inputs/outputs (supports the external-engine
  exemption review).
- MUST NOT claim: "FIDE-approved", "FIDE-endorsed", "certified".
  Approval attaches to a complete THP version, via VCL/SDPC/TAPC —
  a library cannot hold it. No such certification exists for this
  package, and none is asserted anywhere in this repository
  (consistency audit verifies the absence).
- Requires a THP around it: pairing engine, TRF I/O, PTC/RTG CLIs,
  tournament management, UI, persistence, fees, registers.

## Certification boundaries

Library correctness (this repo: formulas, ordering, determinism,
corpus) → TMS compliance (THP vendor: MTB26 coverage, TRF26 I/O,
PTC/RTG, ITDX, cycles) → FIDE approval (TEC+Council: TAPC→FEAP).
Each boundary is a different owner, different artifact, different
evidence. Conflating them is the central error this document exists
to prevent.
