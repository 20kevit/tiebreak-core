# Compatibility

- `pairing-core`: NO dependency in either direction. Both are pure domain
  libs composed by chess-manager. A future shared primitive
  (`{player_id, points, opponents, rating}`) needs evidence before any
  shared contract is introduced.
- chess-manager `domain/pairing/` is a shim over `pairing-core==0.1.0`;
  `domain/tiebreak/` becomes the same pattern over `tiebreak-core==0.1.0`.
- Python `>=3.10`, zero runtime dependencies, `src/` layout, pytest,
  semantic versioning — same standard as pairing-core.
- Endorsed-manager interop (Vega/Swiss-Manager/JaVaFo/bbpPairings):
  reference vectors only; no code reuse (proprietary/JVM/GPL constraints
  documented in the extraction report).
