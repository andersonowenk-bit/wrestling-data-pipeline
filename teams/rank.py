"""Rate every team from all duals, then write the rankings.

Outputs:
  rankings/rankings.csv   full table
  rankings/history.csv    each team's rating after every dual (for charts)
  README.md               top 25 table between the RANKINGS markers
Run: python -m teams.rank
"""
from pathlib import Path

import pandas as pd

from teams.data import load_duals
from teams.elo import TeamElo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "rankings"
START, END = "<!-- RANKINGS:START -->", "<!-- RANKINGS:END -->"


def run_elo(duals: pd.DataFrame):
    elo, history, season = TeamElo(), [], None
    for d in duals.itertuples(index=False):
        if season is not None and d.season != season:
            elo.new_season()
        season = d.season
        elo.update(d.home, d.away, d.home_score, d.away_score, d.neutral, d.winner or None)
        for team in (d.home, d.away):
            history.append({"date": d.date, "season": d.season, "team": team, "rating": elo.get(team)})
    return elo, pd.DataFrame(history)


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
    current = duals.season.max()
    table = pd.DataFrame({"team": list(elo.ratings), "rating": list(elo.ratings.values())})
    table = table.join(season_records(duals, current), on="team")
    table[["wins", "losses"]] = table[["wins", "losses"]].fillna(0).astype(int)
    table["last5"] = table["last5"].fillna("")
    table = table.sort_values("rating", ascending=False).reset_index(drop=True)
    table["rank"] = table.index + 1

    # Rank one week before the most recent dual, for movement arrows
    cutoff = duals.date.max() - pd.Timedelta(days=7)
    before = history[history.date <= cutoff].groupby("team").last()
    if len(before):
        prev = before["rating"].rank(ascending=False, method="first").astype(int)
        table["last_week"] = table["team"].map(prev)
    else:
        table["last_week"] = pd.NA
    table["rating"] = table["rating"].round(0).astype(int)
    return table[["rank", "team", "rating", "wins", "losses", "last5", "last_week"]], history


def movement(row) -> str:
    if pd.isna(row.last_week):
        return "new"
    diff = int(row.last_week) - int(row["rank"])
    return f"up {diff}" if diff > 0 else f"down {-diff}" if diff < 0 else "same"


def markdown(table: pd.DataFrame, duals: pd.DataFrame, n: int = 25) -> str:
    updated = duals.date.max().strftime("%B %-d, %Y")
    lines = [f"Updated through duals on {updated}. {len(duals)} D1 duals rated.", "",
             "| Rank | Team | Rating | Record | Last 5 | Week |", "|---:|---|---:|---|---|---|"]
    for _, r in table.head(n).iterrows():
        lines.append(f"| {r['rank']} | {r.team} | {r.rating} | {r.wins}-{r.losses} | {r.last5} | {movement(r)} |")
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
    if duals.empty:
        print("No duals yet. Add one with: python -m teams.add ...")
        return
    table, history = build_table(duals)
    OUT.mkdir(exist_ok=True)
    table.to_csv(OUT / "rankings.csv", index=False)
    history.to_csv(OUT / "history.csv", index=False)
    update_readme(markdown(table, duals))
    print(markdown(table, duals, n=10))


if __name__ == "__main__":
    main()
