# Integration (chess-manager wiring)

`StandingsService.get_standings` keeps its public shape
(`player_standings / tiebreak_rules / tb_names / rating_changes`) and
delegates calculation+ordering to tiebreak-core through the thin mapper
`application/tournament/tiebreak_adapter.py`:

```
TournamentModel/ParticipantModel/PairingModel/RoundModel
  → TiebreakAdapter.build_inputs()   (9-type table, -1 sentinel, round lookup)
  → tiebreak_core.calculate_all / rank_standings
  → legacy dict shape for templates
```

- Seeding branch (`current_round == 0`) stays in chess-manager.
- Withdrawal filter stays in chess-manager.
- Rating/Elo changes stay in chess-manager (`domain/rating`, not this lib).
- `TIEBREAK_NAMES_FA` for templates is re-exported from
  `tiebreak_core.display` (optional layer; calc path independent).
- Dual-run verification: `tools/check_tiebreak_equivalence.py` compares
  legacy `domain/tiebreak` vs `tiebreak_core` on captured fixtures.
