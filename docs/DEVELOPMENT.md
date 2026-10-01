# Development

```bash
pip install -e .            # zero runtime deps
python -m pytest tests -q   # 40 tests: units + goldens + live old-vs-new + ranking + determinism
```

- Golden capture: `tests/data_goldens.json` (from original
  `domain/tiebreak/calculators.calculate_all`). Live comparison
  (`TestOldVsNewLive`) loads the chess-manager repo source directly when
  present and fails on ANY difference — do not "fix", record a finding.
- Testing strategy: ported units (every calculator) → goldens (values) →
  ranking order → determinism (25× repeat + shuffled) → contract (adapter
  maps real DB rows; verified via chess-manager suite).
- Versioning: semver. Rule changes require NEW `rules_version` strings;
  `legacy-0.1.0` outputs are frozen.
