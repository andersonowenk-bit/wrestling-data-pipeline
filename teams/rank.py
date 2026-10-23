"""Rate every team from all duals, then write the rankings.

Each season starts from the first WrestleStat snapshot of that season (if
there is one), blended with last season's carryover. Dual results then move
the ratings from there.

Outputs:
  rankings/rankings.csv   full table
  rankings/history.csv    each team's rating over time (for charts)
  README.md               top 25 table between the RANKINGS markers
Run: python -m teams.rank
"""
from pathlib import Path

import pandas as pd

from teams.data import load_duals
from teams.elo import TeamElo
from teams.wrestlestat import latest_ranks, season_priors

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "rankings"
START, END = "<!-- RANKINGS:START -->", "<!-- RANKINGS:END -->"
PRIOR_WEIGHT = 0.5  # how much the preseason snapshot counts vs last season's carryover


def run_elo(duals: pd.DataFrame):
    priors = season_priors()
    seasons = sorted(set(duals.season) | set(priors))
    elo, history = TeamElo(), []
    for i, season in enumerate(seasons):
        if i:
            elo.new_season()
        if season in priors:
            snap_date, prior = priors[season]
            for team, r in prior.items():
                elo.ratings[team] = (PRIOR_WEIGHT * r + (1 - PRIOR_WEIGHT) * elo.ratings[team]
                                     if team in elo.ratings else r)
                history.append({"date": pd.Timestamp(snap_date), "season": season, "team": team,
                                "rating": elo.get(team)})
        for d in duals[duals.season == season].itertuples(index=False):
            elo.update(d.home, d.away, d.home_score, d.away_score, d.neutral, d.winner or None)
            for team in (d.home, d.away):
                history.append({"date": d.date, "season": season, "team": team, "rating": elo.get(team)})
    hist = pd.DataFrame(history, columns=["date", "season", "team", "rating"])
    return elo, hist


def season_records(duals: pd.DataFrame, season: str) -> pd.DataFrame:
    s = duals[duals.season == season]
    rows = []
    for d in s.itertuples(index=False):
        if d.home_score == d.away_score and not d.winner:
            continue
        won_home = d.home_score > d.away_score or d.winner == d.home
        rows += [{"team": d.home, "date": d.date, "won": won_home},
                 {"team": d.away, "date": d.date, "won": not won_home}]
    if not rows:
        return pd.DataFrame(columns=["wins", "losses", "last5"])
    df = pd.DataFrame(rows).sort_values("date")
    g = df.groupby("team")["won"]
    return pd.DataFrame({"wins": g.sum().astype(int), "losses": (g.count() - g.sum()).astype(int),
                         "last5": g.apply(lambda s: "".join("W" if w else "L" for w in s.tail(5)))})


def build_table(duals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    elo, history = run_elo(duals)
    current = history.season.max()
    table = pd.DataFrame({"team": list(elo.ratings), "rating": list(elo.ratings.values())})
    table = table.join(season_records(duals, current), on="team")
    table[["wins", "losses"]] = table[["wins", "losses"]].fillna(0).astype(int)
    table["last5"] = table["last5"].fillna("")
    table = table.sort_values("rating", ascending=False).reset_index(drop=True)
    table["rank"] = table.index + 1

    # Rank one week before the latest update, for movement
    cutoff = history.date.max() - pd.Timedelta(days=7)
    before = history[history.date <= cutoff].groupby("team").last()
    if len(before):
        prev = before["rating"].rank(ascending=False, method="first").astype(int)
        table["last_week"] = table["team"].map(prev)
    else:
        table["last_week"] = pd.NA
    table["wrestlestat"] = table["team"].map(latest_ranks())
    table["rating"] = table["rating"].round(0).astype(int)
    cols = ["rank", "team", "rating", "wins", "losses", "last5", "last_week", "wrestlestat"]
    return table[cols], history


def movement(row) -> str:
    if pd.isna(row.last_week):
        return "new"
    diff = int(row.last_week) - int(row["rank"])
    return f"up {diff}" if diff > 0 else f"down {-diff}" if diff < 0 else "same"


def markdown(table: pd.DataFrame, history: pd.DataFrame, duals: pd.DataFrame, n: int = 25) -> str:
    updated = history.date.max().strftime("%B %-d, %Y")
    season = history.season.max()
    played = int((duals.season == season).sum()) if len(duals) else 0
    lines = [f"Updated {updated}. {season} season, {played} D1 duals rated so far.", "",
             "| Rank | Team | Rating | Record | Last 5 | Week | WrestleStat |",
             "|---:|---|---:|---|---|---|---:|"]
    for _, r in table.head(n).iterrows():
        ws = "" if pd.isna(r.wrestlestat) else int(r.wrestlestat)
        lines.append(f"| {r['rank']} | {r.team} | {r.rating} | {r.wins}-{r.losses} | {r.last5} "
                     f"| {movement(r)} | {ws} |")
    return "\n".join(lines)


def update_readme(md: str):
    readme = ROOT / "README.md"
    text = readme.read_text() if readme.exists() else f"{START}\n{END}\n"
    if START not in text:
        text += f"\n{START}\n{END}\n"
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    readme.write_text(f"{head}{START}\n{md}\n{END}{tail}")


def main():
    duals = load_duals()
    table, history = build_table(duals)
    if table.empty:
        print("Nothing to rank yet. Save a WrestleStat snapshot or add a dual first.")
        return
    OUT.mkdir(exist_ok=True)
    table.to_csv(OUT / "rankings.csv", index=False)
    history.to_csv(OUT / "history.csv", index=False)
    update_readme(markdown(table, history, duals))
    print(markdown(table, history, duals, n=10))


if __name__ == "__main__":
    main()
