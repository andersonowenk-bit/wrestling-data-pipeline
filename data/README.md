# Data

| Folder | What goes here | Committed to GitHub? |
|---|---|---|
| `raw/` | Real results you collect (CSV per season or event) | No (gitignored) |
| `sample/` | Small SYNTHETIC dataset so anyone can run the project | Yes |
| `wrestling.duckdb` | The database the pipeline builds | No (rebuild with `make all`) |

## Raw file format

Every CSV in `raw/` should have these columns:

`season, match_date, event, event_type, weight_class, wrestler_a, team_a, wrestler_b, team_b, winner, result_type, score_a, score_b`

- `event_type`: `dual` or `tournament`
- `result_type`: `DEC`, `MD`, `TF`, `FALL`, `FOR` (forfeit), `INJ`, `DQ`
- Rankings go in `raw/official_rankings.csv` with `season, weight_class, rank, wrestler`

## Sources

Document every source here: the site, what you pulled, the date, and a note that you checked its terms of service.

| Source | Data | Terms checked | Notes |
|---|---|---|---|
| _TBD_ | | | |
